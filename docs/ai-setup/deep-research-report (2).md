# Gemini och ChatGPT för MRV‑pipeline med RAG och multimodala bevis

*Datum: 2 mars 2026 (Europe/Stockholm).*

## Executive summary

Den typ av “Gemini‑steg” som beskrivs i den föreslagna MRV‑pipen (retrieval‑augmented standards/regel‑resonemang, bild+text‑analys, programmatisk integration från en worker) är i praktiken **en API‑tjänst**, inte en ren konsumentchatt. För entity["company","Google","technology company"]/entity["company","Alphabet","google parent company"] innebär det att **Gemini Plus/Pro/Ultra‑abonnemang i Gemini‑appen** kan vara användbara för *manuell prototypning* och skrivstöd, men de är **inte den dokumenterade vägen** för att driva en automatiserad, revisionsspårbar pipeline med stabila kvoter, datahanteringsvillkor och (vid behov) SLA. För pipeline‑drift krävs i stället **Gemini Developer API** (minst “Paid”) och/eller **Gemini på Vertex AI** (Enterprise), där funktioner som högre rate limits, cache/batch, enterprise‑säkerhet, och i vissa fall provisionerad throughput formellt stöds. citeturn2view0turn11search5turn1view6turn1view7turn8search3

I EU/EEA är detta extra viktigt: Googles egna villkor för Gemini API säger att man **endast får använda Paid Services när man gör API‑klienter tillgängliga i EEA** (där Sverige ingår). Det gör gratis/“unpaid” upplägg (t.ex. AI Studio utan kopplad billing) olämpligt för en MRV‑worker som betjänar användare/operatörer i Europa. citeturn1view6turn1view2

Motsvarande funktionalitet kan byggas med entity["company","OpenAI","ai company"]:s API: OpenAI API stöder **multimodala inputs** (bilder), **fil‑inputs** (via URL, base64 eller fil‑ID), **RAG via fil‑/vector store (file_search)**, samt **Structured Outputs** för strikt JSON‑schema—vilket är centralt i en MRV‑pipeline där resultat måste vara maskinpars‑ och audit‑vänliga. Däremot är en användares ChatGPT‑abonnemang **inte samma sak som API‑åtkomst**: ChatGPT‑planer är primärt UI‑produkter, medan API används via separat plattform/prissättning. Om din nuvarande ChatGPT‑prenumeration är “Free/Plus/Pro” kan du typiskt göra mycket i UI (inkl. filuppladdning), men en automatiserad backend‑worker kräver i praktiken API‑nycklar och API‑policyer/retentionkontroller. citeturn4search2turn4search6turn4search23turn9search0turn7search5turn1view4

## Slutsats om Gemini Plus kontra Enterprise för MRV‑pipen

### Vad “Gemini Plus” faktiskt ger (i dokumentationen)

Googles nuvarande “AI plans” för individer (på sidan för Gemini‑prenumerationer) visar nivåer som “Google AI Plus/Pro/Ultra” och beskriver tillgång till Gemini‑appen, vissa modeller, Deep Research och andra kreativa funktioner, ofta bundet till lagring (Google One). Det är tydligt positionerat som **individ‑/konsumenterbjudande** och det finns **ingen explicit dokumentation på denna sida som ger API‑nycklar, API‑kvoter, SLA eller enterprise‑data‑villkor** för programmatisk drift. (Det betyder inte att API är “omöjligt”, bara att det inte är det som säljs/garanteras i abonnemanget.) citeturn2view2turn2view0turn9search3

För filhantering i Gemini‑appen finns separata hjälpsidor som beskriver uppladdningsgränser (t.ex. antal filer per prompt och storleksgränser) och att högre AI‑planer kan ge högre uppladdningskvoter. Detta är återigen UI‑/app‑centrerat, inte “drifts‑API”. citeturn0search6

### Vilken Gemini‑nivå som krävs för MRV‑pipens kärnkrav (API + RAG + auditability)

För **programmatisk integration** är den auktoritativa källan Gemini Developer API‑dokumentationen. Där definieras tre nivåer:

- **Free**: begränsad modellåtkomst, gratis tokens, AI Studio‑åtkomst, men innehåll kan användas för att förbättra Googles produkter. citeturn1view2turn1view6  
- **Paid**: högre rate limits, context caching, Batch API (50% kostreduktion), åtkomst till mer avancerade modeller, och “Content not used to improve our products”. citeturn1view2turn1view6turn4search11turn4search5  
- **Enterprise (Vertex AI)**: “Powered by Vertex AI” med valbara enterprise‑förmågor som dedikerad support, avancerad säkerhet/efterlevnad, provisioned throughput och volymrabatter. citeturn1view2turn8search3turn1view7  

Dessutom: Gemini API Additional Terms gör en stark gränsdragning kring datahantering. För Unpaid Services kan innehåll användas för produktförbättring och kan granskas av människor; för Paid Services säger villkoren att Google inte använder prompts/respons/filer för att förbättra sina produkter och att data hanteras under relevant DPA. citeturn1view6

För RAG/grounding finns två vägar, med olika grad av “managed retrieval” och compliance‑kontroller:

- I **Gemini API** kan man använda verktyget **google_search** för att få realtids‑groundade svar med strukturerad `groundingMetadata` (queries, källor, segment‑till‑källa‑mappning) vilket är mycket relevant när man vill minska hallucinationer och förbättra spårbarhet. citeturn10view6turn1view2  
- I **Vertex AI** finns en “Grounding overview” som uttryckligen pekar ut **Grounding with Vertex AI Search** (RAG mot egna dokument), **RAG Engine**, samt **Web Grounding for Enterprise** (webbindex “suitable for highly‑regulated industries” med compliance controls). citeturn10view5turn4search4  

### Slutsats för frågan “finns detta i Gemini Plus?”

För MRV‑pipens kravbild (API‑drift, RAG/grounding, strukturerad output, revisionsspårbarhet, data‑villkor och i många fall enterprise‑säkerhet) är det **inte rimligt att basera sig på Gemini Plus‑abonnemanget**. Den praktiska och dokumenterade vägen är:

- **Gemini Developer API – Paid** för MVP/produktion med standard säkerhetskrav, särskilt i EEA. citeturn1view6turn11search5  
- **Gemini på Vertex AI (Enterprise)** när du behöver SLA, VPC‑kontroller, groundning mot egna datakällor via Vertex AI Search/RAG Engine och provisionerad throughput. citeturn1view7turn6search0turn6search4turn8search3turn10view5  

Gemini Plus kan däremot vara en *bra prototyp‑/författar‑yta* för intern testning av heuristiker och rapportformuleringar—men den är inte det som ger dig den backend‑robusthet som en MRV‑pipeline normalt behöver. citeturn2view2turn11search5

## Jämförelsetabell: Gemini‑nivåer vs ChatGPT‑nivåer för MRV‑pipeline

Tabellerna nedan fokuserar på MRV‑relevanta funktioner: RAG/grounding, fil/bild, API‑åtkomst, rate limiting, retention och säkerhet/efterlevnad. Där källorna inte specificerar exakta gränser markeras “Unspecified” (t.ex. exakta RPM/TPM per kund). citeturn4search1turn7search0

### Gemini (app‑abonnemang, Gemini API, Vertex AI/Enterprise)

| Nivå/produkt | RAG/grounding | Dokument/fil‑ingest | Bildförståelse (multimodal) | API‑åtkomst för worker | Rate limits | Dataanvändning/träning | SLA/enterprise‑drift | Privat nät / “on‑prem connectivity” |
|---|---|---|---|---|---|---|---|---|
| Konsument: “Google AI Plus/Pro/Ultra” (Gemini‑app) | Delvis (t.ex. “Deep Research” i app) men API‑grounding ej beskrivet här | Ja i app (filuppladdning, gränser varierar) | Ja i app (funktioner varierar) | **Unspecified** (ingen explicit API‑rättighet i abonnemangsdokumentet) | App‑kvoter (“AI credits” m.m.), exakta gränser varierar | Konsument/icke‑enterprise dataskydd varierar; enterprise‑skydd kräver särskild licens | Ingen publicerad SLA för app‑abonnemang | Unspecified |
| Gemini Developer API – Free | Kan använda API‑funktioner, men vissa “grounding”/tillägg kan vara begränsade per modell/plan | Ja via API (filer/inputs) | Ja (multimodal) | Ja | Rate limits finns men exakta värden är kontoberoende | **Innehåll kan användas för produktförbättring; ev. human review** | Ingen SLA; prototyp | Unspecified |
| Gemini Developer API – Paid | Ja: context caching, Batch API; grounding med Google Search prissatt/kvoterad | Ja | Ja | **Ja (rekommenderad miniminivå i EEA för prod)** | Högre rate limits än Free | **Prompts/respons/filer används inte för produktförbättring** | Produktionsdrift utan full enterprise‑paket | Unspecified |
| Vertex AI (Gemini) – Enterprise | Ja: Vertex AI Search/RAG Engine, Web Grounding for Enterprise (för reglerade) | Ja, inklusive “grounding with your data” | Ja | Ja (Vertex endpoints) | Skalar + kan reserveras | Google Cloud‑åtaganden om att data inte tränar modeller; ZDR‑alternativ finns | **SLA 99.5% för online inference**; provisioned throughput | **PSC för privat åtkomst från on‑prem**, VPC‑SC för exfiltrationsskydd |

Källor för tabellen ovan inkluderar Gemini prenumerationssida (konsumentplaner), Gemini API‑prissättning och villkor, samt Vertex AI‑dokumentation om grounding, privacy, SLA och privat anslutning. citeturn2view2turn1view2turn1view6turn10view5turn6search4turn1view7turn6search0turn3search4

### ChatGPT‑nivåer och OpenAI API

| Nivå/produkt | RAG/grounding | Dokument/fil‑ingest | Bildförståelse (multimodal) | API‑åtkomst för worker | Rate limits | Dataanvändning/träning | Retention/controlls | Enterprise‑funktioner (SLA, compliance) |
|---|---|---|---|---|---|---|---|---|
| ChatGPT Free/Go/Plus/Pro (UI) | UI‑baserad retrieval av text; “Visual retrieval” för PDF explicit för Enterprise | Ja: filuppladdning; storleks-/kvotgränser | Ja (planberoende), men UI‑läge | **Nej** (separat API‑plattform behövs) | “Reasonable use”/plan‑kvoter; exakta gränser varierar | Individtjänster kan använda innehåll för modellförbättring | Chattar sparas tills du raderar; borttagning normalt inom 30 dagar men undantag finns | Begränsad governance |
| ChatGPT Business (UI) | Som UI; starkare admin/governance än konsument | Ja | Ja | API separat | Planbegränsningar; exakta gränser varierar | **Business‑data tränar inte modeller “by default”** | Retentionpolicys finns (detaljer varierar) | SOC 2 Type 2 stöd; enklare enterprise‑kontroller |
| ChatGPT Enterprise (UI) | Stöd för mer avancerade enterprise‑kopplingar; “Connector registry” & compliance/loggning i plandokument | Ja; **Visual Retrieval för PDF** | Ja | API separat (men enterprise kan ha governance runt) | Större kontext och filstorlek; exakta gränser varierar | **Tränar inte på business‑data “by default”** | Custom retention; compliance‑API‑beteende beskrivet | **Compliance API‑loggplattform**, SCIM/EKM/RBAC, data residency; 24/7 support med SLA |
| OpenAI API (Responses/Tools) | **Ja**: bygg RAG via Vector Store/file_search eller extern store; Structured Outputs | **Ja**: file inputs via base64/URL/fil‑ID | **Ja**: vision | **Ja** | Konto-/tier‑styrda rate limits (dashboard) | **API‑data tränar inte modeller (om ej opt‑in)** | Standard: abuse‑logs upp till 30 dagar; ZDR/modified abuse monitoring via godkännande | API‑drift (SLA ej publikt specificerad); enterprise‑avtal och data residency möjliga |

Källor för tabellen ovan inkluderar ChatGPT‑prissida (Enterprise‑kontroller, compliance/logg), OpenAI Business Data/Enterprise Privacy, fil‑ och retention‑FAQ, Compliance API‑artikel och OpenAI API‑dokumentation för files/vision/RAG/structured outputs. citeturn13view0turn13view3turn9search2turn9search19turn5view1turn5view0turn7search2turn4search2turn4search6turn4search23turn9search0turn5view3

## Integrationsmönster med PostGIS och Mergin Maps

### Basarkitektur (LLM‑agnostisk) för MRV‑worker

Det här mönstret fungerar med både Gemini API/Vertex och OpenAI API: Mergin synkar fältdata (GeoPackage + media) till PostGIS; Postgres NOTIFY triggar en worker; worker kör retrieval (RAG) mot standards‑/juridik‑bibliotek och skickar multimodal prompt (text + foton + referenser); modellen svarar med strikt JSON; resultaten loggas och skrivs tillbaka till PostGIS för revision och rapportpack. citeturn12search0turn12search6turn12search10turn9search0turn9search1

```mermaid
flowchart TD
  A[Mergin Maps (fält)\nGeoPackage + foton] --> B[DB Sync\nGPKG <-> PostGIS]
  B --> C[(PostGIS)]
  C --> D[Trigger: NOTIFY / event table]
  D --> E[Worker\n(Python/Node)]
  E --> F[RAG: hämta relevanta klausuler\n+ SOP + tidigare beslut]
  F --> G{Välj LLM-utförare}
  G -->|Gemini API/Vertex| H[Gemini call\n(multimodal + structured output)]
  G -->|OpenAI API| I[OpenAI call\n(file inputs + vision + structured output)]
  H --> J[JSON-resultat\n(pass/fail/uncertain + citat)]
  I --> J
  J --> K[Auditlogg\nprompt-hash + käll-ID + modellversion]
  K --> C
```

### Integration med Mergin Maps och PostGIS (oavsett LLM)

Mergin DB Sync dokumenteras som ett verktyg för **tvåvägssynk mellan Mergin Maps‑projektets GeoPackage och PostGIS**, där ändringar i PostGIS pushas tillbaka till Mergin‑projekt och ändringar i GeoPackage pushas till PostGIS. Det gör att din MRV‑worker kan jobba mot PostGIS som system of record, medan fältteamet kan fortsätta jobba offline‑först i Mergin. citeturn12search0turn12search12

För händelsedriven automation ger PostgreSQL `LISTEN/NOTIFY` ett inbyggt pub/sub‑mönster där din worker lyssnar på en kanal och får “payload” när en ny observation har skrivits in. Detta kan kombineras med tabellbaserade eventloggar för re‑processing och auditerbar replay. citeturn12search2turn12search6turn12search10

### Integration med Gemini (tre realistiska varianter)

**Variant A: Gemini Developer API (Paid) + egen RAG i Postgres**  
Du indexerar dina Gold Standard‑dokument och interna SOP:ar i en egen vector store (t.ex. pgvector) och skickar endast “top‑k” chunks som kontext. Du använder Structured Outputs i Gemini API för att få ett strikt JSON‑svar som kan sparas i MRV‑datamodellen. citeturn11search5turn9search1turn12search0

**Variant B: Gemini Developer API (Paid) + grounding med Google Search**  
Om du vill ha “källor från webben” med maskinläsbar källa‑till‑text‑mappning kan du aktivera `google_search`‑tool i Gemini API. Svaret inkluderar `groundingMetadata` med queries, web‑källor och segment‑referenser, vilket är mycket användbart för spårbarhet och att minska hallucinationer. För MRV är detta främst relevant för “sekundärkällor” (t.ex. regulatoriska nyheter) och bör separeras från primär evidens. citeturn10view6turn1view2

**Variant C: Vertex AI + Grounding with Vertex AI Search/RAG Engine + enterprise‑kontroller**  
När du vill ha hanterad RAG (indexering, retrieval, governance) och compliance‑inriktade webbkällor (“Web Grounding for Enterprise”) bör du välja Vertex AI. Det ger också formella enterprise‑kontroller såsom VPC Service Controls och Private Service Connect för privat nätväg från on‑prem/hybrid. citeturn10view5turn6search0turn6search4turn1view7

### Integration med ChatGPT/OpenAI (två realistiska varianter)

**Variant D: OpenAI API (Responses) + fil‑inputs + vision + egen RAG**  
OpenAI beskriver att filer kan skickas som base64, som fil‑ID (Files API) eller via extern URL i Responses API. Kombinera med vision‑capabilities för att analysera fältfoton. citeturn4search2turn4search6

**Variant E: OpenAI API + file_search/Vector Store (hanterad retrieval i plattformen)**  
`file_search`‑tool använder en “Vector Store object” och ger ett standardiserat sätt att ladda upp, indexera och göra retrieval över filer. För en MRV‑pipeline kan detta vara en snabb MVP‑väg, men du bör fortfarande spara doc‑ID/chunk‑ID och citation‑mappning till din egen auditlogg. citeturn4search23turn4search31

## Rekommenderad minimal konfiguration och uppgraderingsväg

### Minimal viable configuration (för pilot, demo och jobbpitch)

Eftersom din nuvarande ChatGPT‑prenumeration är **ospecificerad** bör en “vendor‑neutral” MVP beskrivas så här:

- Datainsamling: Mergin Maps → PostGIS via DB Sync. citeturn12search0  
- Worker: enkel Python/Node worker som triggas av NOTIFY. citeturn12search2turn12search6  
- LLM: antingen **Gemini Developer API (Paid)** eller **OpenAI API** (inte UI‑abonnemang). citeturn11search5turn11search17  
- RAG: egen dokumentstore (Postgres/objektlagring) + top‑k chunking; output i strikt JSON via Structured Outputs (både Gemini och OpenAI har JSON‑Schema‑stöd). citeturn9search1turn9search0  
- Logging: spara prompt‑hash, källor (doc_id/chunk_id), modell‑ID och resultat i PostGIS (audit trail). (Detta är en designrekommendation; inte en plattformsfunktion.)  

Det här upplägget kräver inga enterprise‑avtal initialt men är kompatibelt med uppgradering senare.

### När du bör uppgradera och varför

**Till Vertex AI (Gemini Enterprise‑vägen)** när du behöver:  
- SLA (t.ex. 99.5% för Gemini online inference) och ofta förutsägbar kapacitet. citeturn1view7turn8search3  
- Privat/regelstyrd nätanslutning från on‑prem/hybrid (Private Service Connect) och exfiltrationsskydd (VPC Service Controls). citeturn6search4turn6search0  
- Managed RAG med Vertex AI Search/RAG Engine och compliance‑anpassad web grounding. citeturn10view5turn4search4  

**Till ChatGPT Enterprise (OpenAI UI‑enterprise‑vägen)** när kunden kräver:  
- Compliance‑loggplattform och enterprise‑kontroller (SCIM, EKM, RBAC, data residency) i ChatGPT‑arbetsytan. citeturn13view3turn13view0  
- 24/7 support “with SLAs” (detaljnivå på SLA är i praktiken avtalsstyrd och därför “unspecified” offentligt). citeturn8search2  

Observera att ChatGPT Enterprise inte ersätter API‑integration; det kompletterar governance och intern användning. API‑drift sker fortfarande via OpenAI API‑plattformen. citeturn11search17turn7search5

### Kost/effort‑tradeoffs (hög nivå)

- **Gemini Developer API (Paid)** och **OpenAI API** är pay‑as‑you‑go och är ofta billigast att komma igång med, särskilt om du designar RAG så att du skickar liten kontext per request och använder cache/batch för stora körningar. citeturn11search5turn4search5turn11search0turn11search8turn7search5  
- **Vertex AI** tillför extra infra/ops men gör det lättare att uppfylla enterprise‑krav (VPC‑kontroller, privat anslutning, provisioned throughput). citeturn6search4turn8search3turn11search15  
- **ChatGPT Business/Enterprise** tillför governance för människors användning och kan vara en del av en MRV‑organisations “kontorslager” (policy, redaktion, rapport), men är inte ersättning för API‑worker i produktion. citeturn13view3turn9search2  

## Tekniska constraints och risker för revision och integritet

### Datasekretess och retention

På Gemini‑sidan är skillnaden mellan Unpaid och Paid Services explicit: Unpaid kan användas för produktförbättring och kan granskas av människor; Paid Services ska inte användas för produktförbättring och hanteras under DPA. För MRV som kan innehålla personuppgifter (stakeholder‑loggar, foton, GPS) är detta ofta avgörande. citeturn1view6turn11search5

På OpenAI‑sidan gäller att API‑data som standard inte tränar modeller (om du inte opt‑in), men att abuse‑monitoring‑loggar kan sparas upp till 30 dagar; Zero Data Retention eller Modified Abuse Monitoring kräver godkännande för kvalificerade kunder. För MRV bör du behandla detta som en styrningsfråga: “vad skickar vi till modellen” och “vad sparar vi lokalt” måste matcha kundens dataklassning. citeturn5view3turn6search3turn9search19

Även ChatGPT‑UI har viktiga nyanser: filuppladdningar i ChatGPT knyts till chat‑livscykel och raderas normalt inom 30 dagar efter radering av chatten, men retention kan påverkas av säkerhets/juridiska undantag; Enterprise har dessutom särskilda compliance‑API‑beteenden. citeturn5view1turn5view2turn11search6

### Hallucinationer, prompt injection och bevisproveniens

Både Google och OpenAI varnar i sak för att generativa modeller kan ge plausibla men felaktiga svar; en MRV‑pipeline måste därför använda RAG/grounding och kräva citat‑bindning till källor. För Gemini kan du få strukturerade citations via `groundingMetadata` vid Google Search grounding; för interna standarder bör du i stället föredra “grounding with your data” (Vertex AI Search/RAG) eller egen RAG med tydliga doc/chunk‑IDs. citeturn10view6turn10view5turn1view3

För OpenAI API kan Structured Outputs minska “format‑hallucinationer” (felaktig JSON) och file_search/Vector Stores kan ge kontrollerad retrieval; men du behöver fortfarande implementera lokala kontroller (t.ex. att modellen endast får citera källor som faktiskt returnerats av retrieval‑steget). citeturn9search0turn4search23

### Auditability och loggning

För MRV bör du logga minst: (1) modell‑ID/version, (2) retrieval‑källor med hash/ID, (3) prompt‑hash, (4) råsvar + parserat JSON‑resultat, (5) mänsklig sign‑off vid “fail/uncertain”. Detta är en design‑rekommendation, men stöds av att både Gemini och OpenAI erbjuder strikt schema‑output, vilket underlättar robust logging och uppföljning. citeturn9search1turn9search0

Om organisationen också behöver eDiscovery/SIEM‑koppling i själva ChatGPT‑arbetsytan kan ChatGPT Enterprise Compliance API ge åtkomst till loggar/metadata för audit‑ och compliance‑verktyg. citeturn7search2turn13view0

## Pseudokod och retrievaldesign för MRV‑worker

### Pseudokod: Gemini (Paid API) med egen RAG + Structured Outputs

```python
# Pseudokod (Python-stil)

def handle_new_observation(obs_id: str):
    obs = db.fetch_observation(obs_id)                 # PostGIS
    photos = db.fetch_media(obs_id)                    # URIs / bytes
    context_chunks = rag_top_k(
        query=f"{obs.text}\n{obs.location}\n{obs.type}",
        k=10,
        filters={"corpus": ["gold_standard_clauses", "local_law", "SOPs"]}
    )

    schema = {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": ["pass", "fail", "needs_human"]},
            "clause_refs": {"type": "array", "items": {"type": "string"}},
            "missing_evidence": {"type": "array", "items": {"type": "string"}},
            "notes": {"type": "string"}
        },
        "required": ["verdict", "clause_refs", "missing_evidence", "notes"]
    }

    prompt = render_template(
        system_instructions="You are a compliance assistant. Use only provided sources.",
        observation=obs,
        sources=context_chunks
    )

    # Gemini API call (conceptual)
    resp = gemini.generate_content(
        model="gemini-3.1-pro-preview",
        contents=[{"text": prompt}, *photos_as_parts(photos)],
        response_schema=schema  # structured output
    )

    result = parse_json(resp.text)
    db.write_compliance_result(obs_id, result)
    db.write_audit_log(obs_id, prompt_hash=sha256(prompt), sources=context_chunks, model="gemini-3.1-pro-preview")
```

Gemini API stödjer Structured Outputs via JSON‑schema och har även stöd för multimodala uppgifter (bildförståelse). citeturn9search1turn7search3turn7search11turn11search5

### Pseudokod: OpenAI (Responses API) med file inputs + file_search + Structured Outputs

```python
# Pseudokod (Python-stil)

def handle_new_observation(obs_id: str):
    obs = db.fetch_observation(obs_id)
    photo_files = db.fetch_media(obs_id)

    # (A) Indexera/uppdatera standards-dokument i en Vector Store (engång/periodiskt)
    # vector_store_id = ensure_vector_store("gold_standard_and_local_law")

    schema = {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": ["pass", "fail", "needs_human"]},
            "citations": {
                "type": "array",
                "items": {"type": "object", "properties": {
                    "doc_id": {"type": "string"},
                    "chunk_id": {"type": "string"},
                    "quote": {"type": "string"}
                }, "required": ["doc_id", "chunk_id", "quote"]}
            },
            "missing_evidence": {"type": "array", "items": {"type": "string"}},
            "notes": {"type": "string"}
        },
        "required": ["verdict", "citations", "missing_evidence", "notes"]
    }

    resp = openai.responses.create(
        model="gpt-5.2",
        input=[
            {"role": "system", "content": "Compliance assistant. Use only retrieved sources."},
            {"role": "user", "content": [
                {"type": "input_text", "text": obs.to_text()},
                *files_as_input_items(photo_files)  # image/file inputs via file IDs or URLs
            ]}
        ],
        tools=[
            {"type": "file_search", "vector_store_ids": ["vs_gold_standard"]}
        ],
        response_format={"type": "json_schema", "json_schema": schema}
    )

    result = json.loads(resp.output_text)
    db.write_compliance_result(obs_id, result)
    db.write_audit_log(obs_id, model="gpt-5.2", sources=result["citations"])
```

OpenAI dokumenterar (1) fil‑inputs i Responses API, (2) “Images and vision”, (3) file_search via Vector Stores och (4) Structured Outputs som följer supplied JSON Schema. citeturn4search2turn4search6turn4search23turn9search0turn7search1

### Retrievaldesign och promptprinciper (för audit‑vänliga svar)

En MRV‑anpassad retrievaldesign bör i regel:

- Separera corpus i minst två index: (a) standarder/metodik (Gold Standard, VVB‑krav, SOP), (b) lokala lagar/permits, samt (c) tidigare verifierade beslut/NC‑historik.  
- Chunking: hellre “klausul‑centrerade” chunkar (t.ex. 300–900 tokens) med stabila **clause_id** och **doc_version**, än stora narrativa chunkar.  
- Citations: kräva att modellen returnerar **doc_id + chunk_id + kort citat** och att din worker validerar att citatet faktiskt förekommer i chunk‑texten före lagring. (Detta är en kontrollmekanism du implementerar; Gemini Search grounding ger också maskinläsbara citation‑fält när verktyget används.) citeturn10view6turn9search0turn9search1

## Rekommendation för intervjupitch och offerttext om modellval

**Pitch (kort):**  
“Jag designar MRV‑pipelines där LLM:en är utbytbar och revisionsbar: vi kör RAG mot primära standardkällor, tvingar schema‑styrda outputs, loggar källor och prompt‑hash, och har tydliga human sign‑offs. För prototyper kan vi använda OpenAI API eller Gemini API (Paid); för reglerade kunder uppgraderar vi till Vertex AI‑grounding och privat nät/SLA eller till OpenAI Enterprise‑kontroller och retention‑policyer.” citeturn10view5turn1view7turn9search2turn9search19turn11search5turn5view3

**Proposal‑formulering (säker och korrekt):**  
- “LLM‑komponenten drivs via ett API (Gemini Developer API Paid eller OpenAI API) för att möjliggöra eventdriven automation och spårbar logging; UI‑abonnemang används endast för manuell granskning och redaktion.” citeturn11search5turn11search17turn2view2  
- “Känslig MRV‑data behandlas under enterprise‑villkor: på Gemini‑sidan används Paid/Vertex (ingen träning på prompts), på OpenAI‑sidan Business/Enterprise eller API‑kontroller (ingen träning på business‑data som standard, och ZDR vid behov/avtal).” citeturn1view6turn9search2turn5view3turn6search3  
- “För att minska hallucinationer används grounding/RAG; i Gemini kan `groundingMetadata` ge maskinläsbara citat vid Google Search grounding; i övriga fall loggas doc/chunk‑IDs och validerade citat.” citeturn10view6turn10view5turn4search23  

## Primära källor

```text
Gemini (konsumentplaner)
https://gemini.google/subscriptions/
https://one.google.com/about/google-ai-plans/
https://support.google.com/gemini/answer/14903178

Gemini API & villkor (developer)
https://ai.google.dev/gemini-api/docs
https://ai.google.dev/gemini-api/docs/pricing
https://ai.google.dev/gemini-api/terms
https://ai.google.dev/gemini-api/docs/google-search
https://ai.google.dev/gemini-api/docs/structured-output
https://ai.google.dev/gemini-api/docs/image-understanding
https://ai.google.dev/gemini-api/docs/batch-api
https://ai.google.dev/gemini-api/docs/caching

Vertex AI / enterprise (Gemini)
https://cloud.google.com/vertex-ai/generative-ai/sla
https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/overview
https://docs.cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-with-vertex-ai-search
https://docs.cloud.google.com/vertex-ai/generative-ai/pricing
https://docs.cloud.google.com/vertex-ai/docs/general/vpc-service-controls
https://docs.cloud.google.com/vertex-ai/docs/general/vertex-psc-gen-ai

Google Workspace med Gemini (enterprise data protections)
https://support.google.com/a/answer/14130944
https://support.google.com/a/answer/15706919
https://support.google.com/gemini/answer/14620100

Mergin Maps + PostGIS (fält -> backend)
https://merginmaps.com/docs/dev/dbsync/
https://merginmaps.com/docs/dev/integration/

PostgreSQL händelser
https://www.postgresql.org/docs/current/sql-listen.html
https://www.postgresql.org/docs/current/sql-notify.html
https://www.postgresql.org/docs/current/libpq-notify.html

ChatGPT planer och enterprise controls
https://chatgpt.com/pricing/
https://openai.com/business-data/
https://openai.com/enterprise-privacy/
https://help.openai.com/en/articles/9261474-compliance-apis-for-enterprise-customers

OpenAI API (multimodalt, filer, RAG, structured outputs, data controls)
https://developers.openai.com/api/reference/overview/
https://openai.com/api/pricing/
https://developers.openai.com/api/docs/pricing/
https://developers.openai.com/api/docs/guides/your-data/
https://developers.openai.com/api/docs/guides/file-inputs/
https://developers.openai.com/api/docs/guides/images-vision/
https://developers.openai.com/api/docs/assistants/tools/file-search/
https://developers.openai.com/api/docs/guides/structured-outputs/
https://developers.openai.com/api/docs/guides/batch/
https://help.openai.com/en/articles/8555545-file-uploads-faq
https://help.openai.com/en/articles/8983778-chat-and-file-retention-policies-in-chatgpt
```