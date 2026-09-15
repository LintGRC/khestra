"""Fix deliverable names and condense how text for all generated entries."""

import re
import sys
from pathlib import Path

GUIDANCE = Path(__file__).parent / "objective_guidance.py"

import importlib.util as iu

def load(path):
    s = iu.spec_from_file_location("x", path)
    m = iu.module_from_spec(s)
    s.loader.exec_module(m)
    return m

G = load(str(GUIDANCE)).OBJECTIVE_DELIVERABLE_GUIDANCE

# Good names for each control's objectives
OVERRIDE_NAMES = {
    # AC - Access Control
    "AC.L2-3.1.1": {"a": "Authorized user list", "b": "Authorized process list", "c": "Authorized device list",
                     "d": "User access restriction rules", "e": "Process access restriction rules", "f": "Device access restriction rules"},
    "AC.L2-3.1.2": {"a": "Authorized transaction and function list", "b": "Transaction access control rules"},
    "AC.L2-3.1.3": {"a": "Information flow control policy", "b": "Information flow enforcement methods", "c": "CUI source/destination list", "d": "CUI flow authorization policy", "e": "CUI flow enforcement rules"},
    "AC.L2-3.1.4": {"a": "Privileged account list", "b": "Least privilege authorization policy", "c": "Security function list", "d": "Security function authorization policy"},
    "AC.L2-3.1.5": {"a": "Privileged account list", "b": "Least privilege authorization policy", "c": "Security function list", "d": "Security function authorization policy"},
    "AC.L2-3.1.6": {"a": "Privileged account list", "b": "Least privilege authorization policy", "c": "Security function list", "d": "Security function authorization policy"},
    "AC.L2-3.1.7": {"a": "Privileged account list", "b": "Least privilege authorization policy", "c": "Security function list", "d": "Security function authorization policy"},
    "AC.L2-3.1.8": {"a": "Unsuccessful login attempt limit policy", "b": "Unsuccessful login attempt limit configuration"},
    "AC.L2-3.1.9": {"a": "Session lock policy", "b": "Session lock configuration", "c": "Session lock mechanism proof"},
    "AC.L2-3.1.10": {"a": "Inactivity timeout policy", "b": "Inactivity session lock configuration", "c": "Session lock mechanism proof"},
    "AC.L2-3.1.11": {"a": "Session termination policy", "b": "Session termination configuration"},
    "AC.L2-3.1.12": {"a": "Remote access policy", "b": "Remote access configuration", "c": "Remote access session encryption proof", "d": "Remote access session records"},
    "AC.L2-3.1.13": {"a": "Remote access privilege management policy", "b": "Remote privileged access configuration", "c": "Remote privilege execution records"},
    "AC.L2-3.1.14": {"a": "Wireless access policy", "b": "Wireless access configuration"},
    "AC.L2-3.1.15": {"a": "Privileged remote command list", "b": "Remote-accessible information list", "c": "Remote privileged command authorization records", "d": "Remote information access authorization records"},
    "AC.L2-3.1.16": {"a": "Mobile device policy", "b": "Mobile device connection proof"},
    "AC.L2-3.1.17": {"a": "Mobile device connection policy", "b": "Mobile device connection authorization records"},
    "AC.L2-3.1.18": {"a": "Portable storage device policy", "b": "Portable storage limits policy", "c": "Portable storage restriction configuration"},
    "AC.L2-3.1.19": {"a": "Information posting authorization list", "b": "Information flow enforcement methods", "c": "CUI source/destination list", "d": "Information flow authorization list", "e": "Information flow control configuration"},
    "AC.L2-3.1.20": {"a": "External connection list", "b": "External system usage policy", "c": "External connection verification records", "d": "External system verification records", "e": "External connection restriction rules", "f": "External system usage restriction rules"},
    "AC.L2-3.1.21": {"a": "Public information posting policy", "b": "Public posting review process", "c": "Public content review approval records", "d": "Public posting removal process"},
    "AC.L2-3.1.22": {"a": "Public system authorization list", "b": "CUI public posting prohibition policy", "c": "Public content pre-review policy", "d": "Public content CUI review records", "e": "CUI removal mechanism configuration"},

    # AT - Awareness and Training (already manual, no overrides needed)

    # AU - Audit and Accountability
    "AU.L2-3.3.2": {"a": "User action traceability policy", "b": "User action traceability configuration"},
    "AU.L2-3.3.3": {"a": "Logged event type list", "b": "Event content specification", "c": "Logged event review frequency policy", "d": "Logged event review records"},
    "AU.L2-3.3.4": {"a": "Audit failure alert personnel list", "b": "Audit failure types definition", "c": "Audit failure notification records"},
    "AU.L2-3.3.5": {"a": "Audit log reduction process policy", "b": "Audit log correlation capability proof", "c": "Aggregated audit report generation policy", "d": "Aggregated audit report samples"},
    "AU.L2-3.3.6": {"a": "Audit record review frequency policy", "b": "Audit record review, analysis, reporting records"},
    "AU.L2-3.3.7": {"a": "Time stamp source configuration", "b": "Authoritative time source specification", "c": "Clock synchronization records"},
    "AU.L2-3.3.8": {"a": "Privileged audit management policy", "b": "Privileged audit management access configuration", "c": "Audit log functionality configuration", "d": "Audit tool management configuration", "e": "Audit tool protection configuration", "f": "Audit tool integration configuration"},
    "AU.L2-3.3.9": {"a": "Audit information protection policy", "b": "Audit information protection configuration", "c": "Audit log backup configuration"},

    # CA - Security Assessment (already manual, no overrides needed)

    # CM - Configuration Management
    "CM.L2-3.4.1": {"a": "Baseline configuration policy", "b": "Baseline configuration inclusion list", "c": "Baseline configuration records", "d": "System inventory policy", "e": "System inventory requirements", "f": "Inventory records"},
    "CM.L2-3.4.2": {"a": "Baseline configuration management policy", "b": "Baseline configuration update records"},
    "CM.L2-3.4.3": {"a": "Change tracking policy", "b": "Change review records", "c": "Change approval/denial records", "d": "Change logging records"},
    "CM.L2-3.4.4": {"a": "Security impact analysis policy"},
    "CM.L2-3.4.5": {"a": "Physical change restriction definition", "b": "Physical change restriction documentation", "c": "Physical change restriction approval records", "d": "Physical change restriction enforcement config", "e": "Logical change restriction definition", "f": "Logical change restriction documentation", "g": "Logical change restriction approval records", "h": "Logical change restriction enforcement config"},
    "CM.L2-3.4.6": {"a": "Least functionality policy", "b": "Unnecessary function/program/port list", "c": "Unnecessary function/program/port prohibition configuration"},
    "CM.L2-3.4.7": {"a": "Essential program list", "b": "Nonessential program usage policy", "c": "Program restriction rules", "d": "Essential function list", "e": "Nonessential function usage policy", "f": "Function restriction rules", "g": "Essential port list", "h": "Nonessential port usage policy", "i": "Port restriction rules", "j": "Essential protocol list", "k": "Nonessential protocol usage policy", "l": "Protocol restriction rules", "m": "Essential service list", "n": "Nonessential service usage policy", "o": "Service restriction rules"},
    "CM.L2-3.4.8": {"a": "Software usage restriction policy", "b": "Software usage compliance monitoring policy", "c": "Software usage monitoring records"},
    "CM.L2-3.4.9": {"a": "User-installed software policy", "b": "User-installed software enforcement configuration", "c": "User-installed software monitoring records"},

    # IA - Identification and Authentication
    "IA.L2-3.5.1": {"a": "User identification policy", "b": "Process identification policy", "c": "Device identification policy"},
    "IA.L2-3.5.2": {"a": "User authentication configuration", "b": "Process authentication configuration", "c": "Device authentication configuration"},
    "IA.L2-3.5.3": {"a": "Privileged account identification policy", "b": "MFA local access configuration", "c": "MFA network privileged access configuration", "d": "MFA network non-privileged access configuration"},
    "IA.L2-3.5.4": {"a": "Replay-resistant authentication implementation proof"},
    "IA.L2-3.5.5": {"a": "Password complexity policy", "b": "Password change configuration"},
    "IA.L2-3.5.6": {"a": "Identifier inactivity disable period policy", "b": "Identifier inactivity disable records"},
    "IA.L2-3.5.7": {"a": "Password complexity policy", "b": "Password change character policy", "c": "Password complexity enforcement configuration", "d": "Password change character enforcement configuration"},
    "IA.L2-3.5.8": {"a": "Single-use authentication mechanism policy", "b": "Single-use authentication block configuration"},
    "IA.L2-3.5.9": {"a": "Temporary password change policy"},
    "IA.L2-3.5.10": {"a": "Password transmission/storage encryption proof", "b": "Password encryption standard policy"},
    "IA.L2-3.5.11": {"a": "Authentication feedback obscurity configuration"},

    # IR (already manual)
    # MA - Maintenance
    "MA.L2-3.7.1": {"a": "System maintenance schedule and records"},
    "MA.L2-3.7.2": {"a": "Maintenance tool control policy", "b": "Maintenance technique control policy", "c": "Maintenance mechanism control policy", "d": "Maintenance personnel control policy"},
    "MA.L2-3.7.3": {"a": "Off-site maintenance removal policy"},
    "MA.L2-3.7.4": {"a": "Diagnostic media malware check policy"},
    "MA.L2-3.7.5": {"a": "Nonlocal maintenance MFA configuration", "b": "Remote maintenance session termination records"},
    "MA.L2-3.7.6": {"a": "Maintenance personnel supervision policy"},

    # MP (already fixed manually for 3.8.1)
    "MP.L2-3.8.2": {"a": "CUI media access restriction configuration"},
    "MP.L2-3.8.3": {"a": "Media sanitization policy", "b": "Media sanitization records"},
    "MP.L2-3.8.4": {"a": "CUI media classification marking records", "b": "Media distribution limitation marking records"},
    "MP.L2-3.8.5": {"a": "Media transport protection policy", "b": "Media transport protection records"},
    "MP.L2-3.8.6": {"a": "Digital media confidentiality protection policy"},
    "MP.L2-3.8.7": {"a": "Removable media use policy"},
    "MP.L2-3.8.8": {"a": "Portable storage device ownership policy"},
    "MP.L2-3.8.9": {"a": "Backup CUI confidentiality protection policy"},

    # PE - Physical Protection
    "PE.L2-3.10.1": {"a": "Physical access authorization list", "b": "Physical access enforcement configuration", "c": "Visitor control records", "d": "Physical access log records", "e": "Physical access audit records"},
    "PE.L2-3.10.2": {"a": "Facility protection policy", "b": "Infrastructure protection policy", "c": "Facility monitoring records", "d": "Infrastructure monitoring records"},
    "PE.L2-3.10.3": {"a": "Visitor escort policy", "b": "Visitor activity monitoring records"},
    "PE.L2-3.10.4": {"a": "Physical access audit log configuration"},
    "PE.L2-3.10.5": {"a": "Physical access device list", "b": "Physical access device control records", "c": "Physical access device management records"},
    "PE.L2-3.10.6": {"a": "Physical facility protection policy", "b": "Physical facility monitoring policy"},

    # PS (already manual)
    # RA (already manual)
    # SC - System and Communications Protection
    "SC.L2-3.13.1": {"a": "External boundary policy", "b": "Internal boundary policy", "c": "Internal boundary configuration", "d": "External boundary configuration", "e": "Internal boundary protection proof", "f": "External boundary protection proof", "g": "Boundary access configuration", "h": "Boundary traffic limitation configuration"},
    "SC.L2-3.13.2": {"a": "Architecture description", "b": "Architecture design documentation", "c": "Timely architecture update policy", "d": "Architecture update records", "e": "System documentation completeness policy", "f": "System documentation records"},
    "SC.L2-3.13.3": {"a": "Network segregation policy", "b": "Subnet configuration proof", "c": "Public access system segregation configuration"},
    "SC.L2-3.13.4": {"a": "Shared resource information control policy"},
    "SC.L2-3.13.5": {"a": "Network disconnect capability policy", "b": "Network disconnect capability proof"},
    "SC.L2-3.13.6": {"a": "Network communications monitoring policy", "b": "Network communications monitoring records"},
    "SC.L2-3.13.7": {"a": "Remote device simultaneous connection policy"},
    "SC.L2-3.13.8": {"a": "Cryptographic key management policy", "b": "Cryptographic key management configuration", "c": "Cryptographic key escrow policy"},
    "SC.L2-3.13.9": {"a": "Network connection management policy", "b": "Network connection authorization records", "c": "Network connection authorization completion records"},
    "SC.L2-3.13.10": {"a": "Cryptographic key generation/management policy", "b": "Cryptographic key management configuration"},
    "SC.L2-3.13.11": {"a": "FIPS-validated cryptography implementation proof"},
    "SC.L2-3.13.12": {"a": "Collaborative computing device identification policy", "b": "Collaborative computing device indication policy", "c": "Collaborative device disabling configuration"},
    "SC.L2-3.13.13": {"a": "Mobile code usage policy", "b": "Mobile code enforcement configuration"},
    "SC.L2-3.13.14": {"a": "Voice-over-IP policy", "b": "VoIP usage restriction configuration"},
    "SC.L2-3.13.15": {"a": "Communication session authenticity protection proof"},
    "SC.L2-3.13.16": {"a": "CUI at-rest confidentiality protection proof"},

    # SI - System and Information Integrity
    "SI.L2-3.14.1": {"a": "Flaw identification timeframe policy", "b": "Flaw identification records", "c": "Flaw reporting timeframe policy", "d": "Flaw reporting records", "e": "Flaw correction timeframe policy", "f": "Flaw correction records"},
    "SI.L2-3.14.2": {"a": "Flaw remediation process policy", "b": "Flaw remediation records", "c": "Patch testing process policy", "d": "Patch testing records", "e": "Software/firmware update restriction policy"},
    "SI.L2-3.14.3": {"a": "Malicious code protection policy", "b": "Malware protection configuration", "c": "Malware scan configuration", "d": "Malware scan records", "e": "Malware update mechanism configuration"},
    "SI.L2-3.14.4": {"a": "Malicious code signature update policy"},
    "SI.L2-3.14.5": {"a": "System file integrity monitoring policy", "b": "System file integrity monitoring records"},
    "SI.L2-3.14.6": {"a": "System attack monitoring configuration", "b": "Inbound attack monitoring configuration", "c": "Outbound attack monitoring configuration"},
    "SI.L2-3.14.5": {"a": "System file integrity monitoring policy", "b": "System file integrity monitoring records", "c": "External file integrity check configuration"},
    "SI.L2-3.14.7": {"a": "System security alert policy", "b": "Security alert configuration", "c": "Security alert configuration", "d": "Security alert configuration"},
}

def condensed_how(eit_data, kind):
    """Create a concise how text from the EIT data."""
    if not eit_data:
        return "Consult NIST SP 800-171A assessment procedures."
    eit = []
    
    def _clean(txt):
        if not txt:
            return ""
        t = txt.replace("[SELECT FROM:", "").strip()
        t = t.rstrip("]").rstrip(".]").strip()
        return t.replace("\n", " ").strip()
    
    if kind == "policy":
        examine = eit_data.get("examine", "")
        e = _clean(examine)
        items = [x.strip() for x in e.split(";") if x.strip()]
        # Pick first 3-4 items from examine list
        selected = items[:3]
        if selected:
            # Try to pick meaningful items — prefer policy/procedure items
            meaningful = [x for x in selected if not x.startswith("other ") and len(x) > 5]
            eit.append("Examine: " + "; ".join(meaningful[:3]) if meaningful else "; ".join(selected))
    elif kind == "config":
        test = eit_data.get("test", "")
        t = _clean(test)
        items = [x.strip() for x in t.split(";") if x.strip()]
        test_items = [x for x in items if not x.startswith("other ")][:2]
        if test_items:
            eit.append("Test: " + "; ".join(test_items))
    else:  # evidence
        examine = eit_data.get("examine", "")
        test = eit_data.get("test", "")
        e = _clean(examine)
        t = _clean(test)
        e_items = [x.strip() for x in e.split(";") if x.strip() and not x.startswith("other ")][:2]
        t_items = [x.strip() for x in t.split(";") if x.strip() and not x.startswith("other ")][:2]
        if e_items:
            eit.append("Examine: " + "; ".join(e_items))
        if t_items:
            eit.append("Test: " + "; ".join(t_items))
    
    return " ".join(eit) if eit else "Consult NIST SP 800-171A assessment procedures."


def fix():
    # Load EIT reference data
    ref_path = Path(__file__).parent / "nist_eit_reference.py"
    ref_mod = load(str(ref_path))
    REF = ref_mod.NIST_EIT_REFERENCE
    
    for cid in sorted(G):
        if cid not in OVERRIDE_NAMES:
            continue
        overrides = OVERRIDE_NAMES[cid]
        for letter in G[cid]:
            if letter in overrides:
                G[cid][letter]["deliverable"] = overrides[letter]
    
    # Fix how text for all entries using EIT reference
    for cid in sorted(G):
        eit_data = REF.get(cid, {})
        for letter, entry in G[cid].items():
            kind = entry.get("kind", "evidence")
            entry["how"] = condensed_how(eit_data, kind)
    
    # Write back
    import ast, tokenize, io
    import os
    
    ts = tokenize.generate_tokens(io.StringIO(open(str(GUIDANCE)).read()).readline)
    
    # Build output
    output = []
    with open(str(GUIDANCE)) as f:
        content = f.read()
    
    # Find the opening { of OBJECTIVE_DELIVERABLE_GUIDANCE dict
    start = content.find("OBJECTIVE_DELIVERABLE_GUIDANCE")
    if start < 0:
        print("ERROR: Could not find OBJECTIVE_DELIVERABLE_GUIDANCE")
        return
    brace_start = content.find("{", start)
    if brace_start < 0:
        print("ERROR: Could not find opening brace")
        return
    
    # Preserve header (docstring + type annotation + dict start)
    new_file = content[:brace_start+1] + "\n"
    
    for cid in sorted(G):
        new_file += f'    "{cid}": {{\n'
        for letter in sorted(G[cid]):
            e = G[cid][letter]
            new_file += f'        "{letter}": {{\n'
            new_file += f'            "deliverable": {e["deliverable"]!r},\n'
            new_file += f'            "how": {e["how"]!r},\n'
            new_file += f'            "kind": {e["kind"]!r},\n'
            new_file += f'        }},\n'
        new_file += f'    }},\n'
    new_file += "}\n"
    
    with open(str(GUIDANCE), "w") as f:
        f.write(new_file)
    print(f"Written {len(G)} controls, {sum(len(v) for v in G.values())} objectives")


if __name__ == "__main__":
    fix()
