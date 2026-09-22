def parse_objections(raw):
    if not isinstance(raw, str) or not raw.strip():
        return []

    # 1. Se il testo usa la sintassi [Obiezione] -> Risposta (usata nel campo principale di Fabula)
    if "[" in raw and "]" in raw:
        out = []
        for block in re.split(r"\|\|", raw):
            block = block.strip().strip(",")
            if not block:
                continue
            m = re.match(r"^\s*\[(.+?)\]\s*->\s*(.*)$", block, flags=re.S)
            if m:
                out.append({"q": clean(m.group(1)), "a": clean(m.group(2))})
            else:
                out.append({"q": "", "a": clean(block)})
        if out:
            return out

    # 2. Se usa il formato con virgolette caporali «...»
    if "«" in raw:
        cleaned = clean(raw)
        cleaned = re.sub(
            r"^(Возражение|Заперечення|Iebildums|Obiekcja)?\s*(Стратегия\s+преодоления|Pārvarēšanas\s+stratēģija)?\s*",
            "",
            cleaned,
            flags=re.I,
        )

        out = []
        # Estrae tutti i blocchi del tipo «Domanda» Risposta
        pattern = re.compile(r"«([^»]+)»\s*([^«]+)")
        matches = pattern.findall(cleaned)

        if matches:
            for q_raw, a_raw in matches:
                q = q_raw.strip(" \t\n\r,;«»")
                a = a_raw.strip(" \t\n\r,;«»")

                # Se la Strategy Word era finita INSIDE la prima parte delle virgolette (come Festone):
                strat_found = None
                for sw in STRATEGY_WORDS:
                    m = re.search(r"\b" + re.escape(sw) + r"\b", q)
                    if m:
                        strat_found = (m.start(), m.end(), sw)
                        break

                if strat_found:
                    actual_q = q[: strat_found[0]].strip(" \t\n\r,;«»")
                    actual_a = (q[strat_found[1] :] + " " + a).strip(
                        " \t\n\r,;«»"
                    )
                    q, a = actual_q, actual_a

                if q and a:
                    if not a.endswith("."):
                        a += "."
                    out.append({"q": q, "a": a})
            if out:
                return out

    # Fallback per separatore pipe ||
    if "||" in raw:
        out = []
        for block in re.split(r"\|\|", raw):
            block = block.strip()
            if block:
                out.append({"q": "", "a": clean(block)})
        if out:
            return out

    return [{"q": "", "a": clean(raw)}]
