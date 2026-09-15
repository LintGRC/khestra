type Props = {
  title: string;
  summary?: string;
};

export default function PageIntro({ title, summary }: Props) {
  return (
    <header className="page-intro">
      <h2 className="page-intro-title">{title}</h2>
      {summary && <p className="muted page-intro-summary">{summary}</p>}
    </header>
  );
}
