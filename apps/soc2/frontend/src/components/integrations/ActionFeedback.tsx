type Props = {
  message: string;
  onDismiss: () => void;
};

export default function ActionFeedback({ message, onDismiss }: Props) {
  const isError = message.startsWith("Error") || message.includes("failed") || message.includes("required");

  return (
    <div className={`banner integrations-feedback${isError ? " warning" : " info"}`} role="status">
      <span>{message}</span>
      <button type="button" className="btn-link integrations-feedback-dismiss" onClick={onDismiss}>
        Dismiss
      </button>
    </div>
  );
}
