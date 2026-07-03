import typer
from typing import Optional
from rab_q.client import Messaging
import json

app = typer.Typer(help="Enterprise MQ Command Line Interface")

@app.command()
def publish(
    queue: str = typer.Argument(..., help="The queue to publish to"),
    message: str = typer.Argument(..., help="JSON string of the message body"),
    api_key: str = typer.Option("ank@8250255103#sark_$", help="API Key for the SDK")
):
    """Publish a message to a queue."""
    try:
        data = json.loads(message)
    except json.JSONDecodeError:
        typer.secho("Error: Message must be a valid JSON string.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
        
    try:
        mq = Messaging(api_key=api_key)
        mq.publish(queue, data)
        mq.shutdown()
        typer.secho(f"Successfully published to '{queue}'", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Failed to publish: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command()
def doctor():
    """Check the health and configuration of the SDK."""
    typer.secho("Checking rab_q SDK health...", fg=typer.colors.CYAN)
    
    try:
        mq = Messaging(api_key="ank@8250255103#sark_$")
        typer.secho("✓ License Validated", fg=typer.colors.GREEN)
        typer.secho("✓ Connected to RabbitMQ successfully", fg=typer.colors.GREEN)
        mq.shutdown()
    except Exception as e:
        typer.secho(f"✗ Health check failed: {e}", fg=typer.colors.RED)

if __name__ == "__main__":
    app()
