from email import policy
from email.parser import BytesParser
from pathlib import Path


def parse_eml_file(file_path: str) -> dict:

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() != ".eml":
        raise ValueError("The provided file must have a .eml extension.")

    # Parse the email first
    with path.open("rb") as file:
        message = BytesParser(policy=policy.default).parse(file)

    plain_text_parts = []
    html_parts = []
    attachments = []

    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            disposition = part.get_content_disposition()
            filename = part.get_filename()

            # Handle attachments
            if filename or disposition == "attachment":
                attachments.append(
                    {
                        "filename": filename or "unnamed_attachment",
                        "content_type": content_type,
                        "disposition": disposition or "attachment",
                    }
                )
                continue

            # Skip multipart container sections
            if content_type.startswith("multipart/"):
                continue

            try:
                content = part.get_content()
            except Exception:
                continue

            if content_type == "text/plain":
                plain_text_parts.append(str(content))

            elif content_type == "text/html":
                html_parts.append(str(content))

    else:
        content_type = message.get_content_type()

        try:
            content = message.get_content()
        except Exception:
            content = ""

        if content_type == "text/plain":
            plain_text_parts.append(str(content))

        elif content_type == "text/html":
            html_parts.append(str(content))

    return {
        "from": message.get("From", ""),
        "to": message.get("To", ""),
        "reply_to": message.get("Reply-To", ""),
        "return_path": message.get("Return-Path", ""),
        "subject": message.get("Subject", ""),
        "date": message.get("Date", ""),
        "message_id": message.get("Message-ID", ""),
        "authentication_results": message.get(
            "Authentication-Results",
            "",
        ),
        "received_spf": message.get("Received-SPF", ""),
        "plain_text_body": "\n".join(plain_text_parts).strip(),
        "html_body": "\n".join(html_parts).strip(),
        "attachments": attachments,
    }