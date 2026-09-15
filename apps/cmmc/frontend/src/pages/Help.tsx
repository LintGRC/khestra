import { api } from "../api";
import HelpPage from "@shared/settings/HelpPage";

export default function HelpPageWrapper() {
  return <HelpPage getHelp={() => api.help()} />;
}
