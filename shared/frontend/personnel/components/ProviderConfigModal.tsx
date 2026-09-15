import ProviderConfigForm from "./ProviderConfigForm";

export default function ProviderConfigModal({ provider, onClose }: { provider: string; onClose: () => void }) {
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-panel import-dialog-panel" onClick={(e) => e.stopPropagation()}>
        <ProviderConfigForm provider={provider} onSaved={onClose} onBack={onClose} />
      </div>
    </div>
  );
}
