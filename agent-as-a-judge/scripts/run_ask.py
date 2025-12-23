import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.emoji import Emoji
import io


from agent_as_a_judge.agent import JudgeAgent
from agent_as_a_judge.config import AgentConfig

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
console = Console()


def main(agent_config: AgentConfig, initial_question: str, logger: logging.Logger):
    workspace = agent_config.workspace_dir
    judge_agent = JudgeAgent(
        workspace=workspace,
        instance=None,
        judge_dir=agent_config.judge_dir,
        trajectory_file=None,
        config=agent_config,
    )

    handle_question(judge_agent, initial_question, logger)
    while True:
        next_question = input(
            "\nDo you have another question? (Enter question or type 'no' to exit): "
        ).strip()
        if next_question.lower() == "no":
            break
        handle_question(judge_agent, next_question, logger)


def handle_question(judge_agent: JudgeAgent, question: str, logger: logging.Logger):

    response = judge_agent.ask_anything(question)
    display_qa(question, response, logger)


def display_qa(question: str, response: str, logger: logging.Logger):

    question_markdown = f"{Emoji('question')} **Question**\n{question}"
    response_markdown = f"{Emoji('speech_balloon')} **Response**\n{response}"

    panel_content = f"{question_markdown}\n\n---\n\n{response_markdown}"
    panel = Panel(
        Markdown(panel_content),
        title="[bold magenta]🔍 Question and Response[/bold magenta]",
        border_style="bold cyan",
        title_align="center",
        padding=(1, 2),
    )

    with io.StringIO() as buf:
        temp_console = Console(file=buf, width=80, record=True)
        temp_console.print(panel)
        formatted_message = buf.getvalue()
    console.print(panel)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--workspace", type=str, required=True, help="Path to the workspace directory"
    )
    parser.add_argument(
        "--question", type=str, required=True, help="Initial question to ask the agent"
    )
    parser.add_argument(
        "--include_dirs",
        nargs="+",
        default=None,
        help="Directories to include in search",
    )
    parser.add_argument(
        "--exclude_dirs",
        nargs="+",
        default=[
            "__pycache__",
            "env",
            ".git",
            "venv",
            "logs",
            "output",
            "tmp",
            "temp",
            "cache",
            "data",
        ],
        help="Directories to exclude in search",
    )
    parser.add_argument(
        "--exclude_files",
        nargs="+",
        default=[".DS_Store"],
        help="Files to exclude in search",
    )

    return parser.parse_args()


if __name__ == "__main__":
    load_dotenv()
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    args = parse_arguments()
    workspace_dir = Path(args.workspace)
    judge_dir = workspace_dir / "judge"

    agent_config = AgentConfig(
        include_dirs=args.include_dirs,
        exclude_dirs=args.exclude_dirs,
        exclude_files=args.exclude_files,
        setting="black_box",
        planning="comprehensive (no planning)",
        judge_dir=judge_dir,
        workspace_dir=workspace_dir,
        instance_dir=None,
        trajectory_file=None,
    )

    main(
        agent_config=agent_config,
        initial_question=args.question,
        logger=logger,
    )
