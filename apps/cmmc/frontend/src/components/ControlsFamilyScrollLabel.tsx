type Props = {
  prefix: string;
  name: string;
};

export default function ControlsFamilyScrollLabel({ prefix, name }: Props) {
  return (
    <div className="controls-family-scroll-label">
      {prefix ? <span className="control-id-text">{prefix}</span> : null}
      {name ? <span className="controls-family-scroll-name">{prefix ? " · " : ""}{name}</span> : null}
    </div>
  );
}
