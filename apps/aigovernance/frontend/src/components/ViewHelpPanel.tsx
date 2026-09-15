import { Link } from "react-router-dom";

export type HelpViewKey = string;

type Props = { viewKey?: HelpViewKey };

export default function ViewHelpPanel({ viewKey: _ }: Props) {
  return (
    <p className="muted" style={{ fontSize: "0.85rem" }}>
      See <Link to="/help">Help &amp; FAQ</Link> for more information.
    </p>
  );
}
