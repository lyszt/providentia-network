import datetime
import json
import os
import struct
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any, Optional, Tuple

from pydantic import BaseModel, Field


class ContextStruct(BaseModel):
    user_enquiry: str = Field(
        description="The raw, unaltered text query received from the user."
    )
    user_name: str = Field(
        description="The display name or identifier for the user who sent the query."
    )
    needs_command: bool = Field(
        description="A flag indicating if the query requires an external tool or command to be executed."
    )
    client_platform: str = Field(
        description="The source application the query originated from."
    )
    category: str = Field(
        description="The general classification or topic of the user's enquiry."
    )
    steps_for_completion: str = Field(
        description="The high-level plan or steps generated for the AI agent to follow."
    )
    date_of_request: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="The timestamp marking when this context object was created."
    )
    is_done_thinking: bool = Field(
        description="Are these enough steps of thought or should we continue?"
    )
    regrets_choice: bool = Field(
        description="Are you going the right way? Should you return back to a previous step?"
    )


class ThinkingProcessError(RuntimeError):
    """Raised when the C++ thinking process reports an error or fails."""


CPP_DIR = Path(__file__).resolve().parent / "Kievan Rus"
CPP_BINARY_NAME = "kievan_rus_thinker"
if os.name == "nt":
    CPP_BINARY_NAME += ".exe"
CPP_BINARY = CPP_DIR / CPP_BINARY_NAME


def _locate_env_file() -> Optional[Path]:
    """Return the most likely .env file path, if it exists."""
    explicit = os.environ.get("KIEVAN_RUS_ENV_PATH")
    if explicit:
        candidate = Path(explicit)
        if candidate.exists():
            return candidate
    project_root = Path(__file__).resolve().parents[2]
    default_env = project_root / ".env"
    if default_env.exists():
        return default_env
    return None


def _ensure_cpp_binary() -> Path:
    """
    Ensure the C++ assistant is compiled. If the binary is missing or older than
    the source file, attempt to rebuild it. This assumes a system compiler and libcurl.
    """
    try:
        sources = sorted(CPP_DIR.glob("*.cpp"))
        headers = list(CPP_DIR.glob("*.hpp"))
    except OSError as exc:
        raise ThinkingProcessError(f"Unable to enumerate C++ sources: {exc}") from exc

    if not sources:
        raise ThinkingProcessError("No C++ source files found for the thinking engine.")

    latest_timestamp = 0.0
    for path in sources + headers:
        try:
            latest_timestamp = max(latest_timestamp, path.stat().st_mtime)
        except OSError:
            continue

    if CPP_BINARY.exists():
        try:
            if CPP_BINARY.stat().st_mtime >= latest_timestamp:
                return CPP_BINARY
        except OSError:
            pass

    compile_command = [
        "g++",
        "-std=c++17",
        "-O2",
        *[path.name for path in sources],
        "-lcurl",
        "-o",
        str(CPP_BINARY),
    ]

    try:
        subprocess.run(
            compile_command,
            check=True,
            cwd=str(CPP_DIR),
        )
    except FileNotFoundError as exc:
        raise ThinkingProcessError(
            "C++ compiler (g++) not found. Install a C++17-compatible compiler to build the thinking engine."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise ThinkingProcessError(
            f"Failed to compile C++ thinking engine. Command: {' '.join(compile_command)}"
        ) from exc

    return CPP_BINARY


def _read_binary_payload(path: Path) -> Tuple[dict[str, Any], str]:
    """
    The binary payload is encoded as:
        status (1 byte)
        context_length (4 bytes, big-endian)
        context payload (context_length bytes, UTF-8)
        summary_length (4 bytes, big-endian)
        summary payload (summary_length bytes, UTF-8)
    """
    with path.open("rb") as stream:
        status_raw = stream.read(1)
        if len(status_raw) != 1:
            raise ThinkingProcessError("Malformed output from C++ thinking engine (missing status byte).")

        status = status_raw[0]

        context_len_bytes = stream.read(4)
        if len(context_len_bytes) != 4:
            raise ThinkingProcessError("Malformed output from C++ thinking engine (missing context length).")
        context_length = struct.unpack(">I", context_len_bytes)[0]
        context_payload = stream.read(context_length)
        if len(context_payload) != context_length:
            raise ThinkingProcessError("Malformed output from C++ thinking engine (truncated context payload).")

        summary_len_bytes = stream.read(4)
        if len(summary_len_bytes) != 4:
            raise ThinkingProcessError("Malformed output from C++ thinking engine (missing summary length).")
        summary_length = struct.unpack(">I", summary_len_bytes)[0]
        summary_payload = stream.read(summary_length)
        if len(summary_payload) != summary_length:
            raise ThinkingProcessError("Malformed output from C++ thinking engine (truncated summary payload).")

    context_text = context_payload.decode("utf-8")
    summary_text = summary_payload.decode("utf-8")

    if status != 0:
        raise ThinkingProcessError(context_text or "C++ thinking engine reported an error.")

    try:
        context_obj = json.loads(context_text)
    except json.JSONDecodeError as exc:
        raise ThinkingProcessError("Unable to parse JSON generated by C++ thinking engine.") from exc

    if not isinstance(context_obj, dict):
        raise ThinkingProcessError("Unexpected JSON structure from C++ thinking engine.")

    return context_obj, summary_text


def _invoke_cpp_thinker(message: str, iteration: int, summarized_thought: str) -> Tuple[dict[str, Any], str]:
    binary_path = _ensure_cpp_binary()
    env_path = _locate_env_file()

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        output_path = Path(tmp.name)

    command = [
        str(binary_path),
        "--message",
        message,
        "--output",
        str(output_path),
        "--iteration",
        str(iteration),
    ]
    if summarized_thought:
        command.extend(["--summary", summarized_thought])
    if env_path:
        command.extend(["--env", str(env_path)])

    try:
        subprocess.run(command, check=True, cwd=str(CPP_DIR))
        return _read_binary_payload(output_path)
    except subprocess.CalledProcessError as exc:
        raise ThinkingProcessError(
            f"C++ thinking engine execution failed with exit code {exc.returncode}."
        ) from exc
    finally:
        try:
            output_path.unlink(missing_ok=True)
        except AttributeError:
            if output_path.exists():
                output_path.unlink()


class ThinkingManager:
    def __init__(
        self,
        message,
        iteration: int = 0,
        previous: Optional["ThinkingManager"] = None,
        summarized_thought: str = "",
    ):
        self.next = []
        self.id = str(uuid.uuid4())

        self.previous = previous
        if previous is not None:
            previous.next.append(self)

        self.message = message
        self.iteration = iteration + 1
        self.max_iterations = 15

        try:
            raw_context, summarize_thought = _invoke_cpp_thinker(
                message=message,
                iteration=self.iteration,
                summarized_thought=summarized_thought,
            )
        except ThinkingProcessError as exc:
            print(f"Error running C++ thinking engine: {exc}")
            self.context = None
            return

        try:
            command_obj = ContextStruct.model_validate(raw_context)
        except Exception as exc:
            print(f"Validation error parsing context: {exc}")
            self.context = None
            return

        self.context = command_obj.model_dump()

        if not self.context.get("is_done_thinking", False) and self.iteration <= self.max_iterations:
            ThinkingManager(
                message=message,
                iteration=self.iteration,
                previous=self,
                summarized_thought=summarize_thought,
            )

    def build_thought_tree_prompt(self) -> str:
        """
        Builds a text representation of the entire thought process
        by traversing up to the root, then recursively printing the tree.
        """

        root = self
        while root.previous is not None:
            root = root.previous

        output_lines = []
        self._build_tree_recursive(root, 0, output_lines)
        print("\n".join(output_lines))
        return "\n".join(output_lines)

    def _build_tree_recursive(self, node: "ThinkingManager", depth: int, output_lines: list):
        """
        Recursively traverses the thought tree and build the string.
        """
        if node.context is None:
            return

        indent = "  " * depth
        plan = node.context.get("steps_for_completion", "No plan generated.")
        regrets = node.context.get("regrets_choice", False)

        prefix = ""
        if regrets:
            prefix = "[REGRETTED] "
        elif node.context.get("is_done_thinking", False):
            prefix = "[FINAL] "

        output_lines.append(f"{indent}{prefix}Thought (ID: {node.id}, Depth: {depth}): {plan}")

        for child_node in node.next:
            self._build_tree_recursive(child_node, depth + 1, output_lines)

    def generate_self_prompt(self):
        thought_tree_string = self.build_thought_tree_prompt()

        root = self
        while root.previous is not None:
            root = root.previous
        original_user_message = root.message

        return f"""
        [ ORIGINAL USER MESSAGE ]
        {original_user_message}

        [ I need to respond to this user. ]
        [ Here is my complete thought process on how to answer: ]
        {thought_tree_string}

        [ Based on this plan, provide the final response. Follow the *last* thought. ]
        """
