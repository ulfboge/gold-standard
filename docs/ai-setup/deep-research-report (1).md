# Strategi för Gold Standard MRV med Mergin Maps och automatiserad pipeline

## Sammanfattning för intervju och förslag

Det här upplägget är en “fält-till-audit”-pipeline som gör två saker samtidigt: (1) den producerar spårbara, verifierbara MRV-underlag som är direkt mappade till Gold Standard-dokumentation och fjärranalyskrav, och (2) den minimerar friktion i fält genom Mergin Maps-synk och automatiserad QA/rapportering. Kärnidén är att all fältdata samlas i Mergin Maps (GeoPackage + media), replikeras till en robust backend (PostGIS), och triggar en händelsedriven worker som kör valideringar, skapar “audit trail”-loggar och genererar färdiga bevispaket för VVB och Gold Standards Assurance Platform/Registry-processer. citeturn31search0turn8view0turn22view0

Gold Standard-kraven styr **vad** som måste kunna bevisas: en Monitoring & Reporting Plan med tydliga parametrar, frekvens, metod, ansvariga och QC; ett sammanhängande evidens- och “audit trail”-spår som täcker hela monitoreringsperioden; samt, för LUF/Blue Carbon, explicita krav på GIS-lager och fjärranalysupplägg (t.ex. tidsstämplade scener 10 år före startdatum och vid startdatum, samt klassificeringsnoggrannhet och dokumenterade kontrollpunkter). citeturn3view0turn4view0turn12view0turn8view0turn5search3

Gemini (som stöd för “legal/standards reasoning”) placeras inte som en “domare” över data, utan som en **beslutsstödsmodell**: den flaggar luckor (saknade obligatoriska fält/evidens), föreslår åtgärder och hjälper till att formulera revisionsspårbara motiveringar och avsnitt till rapportmallar. Det är förenligt med att Gold Standard uttryckligen beskriver att ICT i remote audit-tekniker kan omfatta bl.a. AI, men att själva revisionsopinionen ligger hos VVB och processen följer Gold Standards krav. citeturn9view0turn20view0turn8view0

En intervjupitch i en mening: **“Jag bygger MRV-system som är audit-ready från dag 1: fältdata → automatiserad QA → spårbara bevispaket och GIS/RS-underlag som matchar Gold Standards klausuler, med kontrollerad AI som minskar manuellt arbete utan att äventyra integritet.”** citeturn8view0turn3view0turn12view0turn21view0

## Gold Standard-krav som påverkar fjärranalys och fältdata

Gold Standard kräver att projekt har en Monitoring & Reporting Plan som minst beskriver (a) vilka parametrar som monitoreras, (b) frekvens, (c) insamlingsmetod och ansvariga, (d) kvalitetskontroll samt (e) etiska begränsningar. I praktiken betyder det att fältformulär och datamodell måste bära “metadata om mätningen”, inte bara värdet. citeturn3view0turn2view0

Gold Standard ställer också **tekniska krav på kartor**: kartor ska bl.a. ha projektnamn/ID, legend, skala, nordpil, koordinatsystem (ex. WGS84) och **information om satellit- eller flygbild (datum, upplösning, datakälla)**. En pipeline som producerar kartbilagor måste därför automatiskt skapa och lagra dessa metadata så att de kan återanvändas i PDD/Monitoring Report och vid audit. citeturn4view0turn2view0

För verifiering lyfter Gold Standard en central princip: VVB ska bekräfta att det finns ett **audit trail** som innehåller “evidence and records” som kan validera/invalidatiera rapporterade siffror; VVB ska dessutom bedöma evidensens täckning över tid och korschecka mot andra källor, och “shall only certify … based on verifiable evidence”. Det driver designen mot (1) oföränderliga loggar, (2) tydlig koppling observation → bilaga → beräkning, och (3) reproducerbarhet. citeturn8view0turn7view3

### Fjärranalys och “relaterade områden” i LUF

I Land Use & Forests Activity Requirements finns ett detaljerat fjärranalysprotokoll för att fastställa eligible areas via en forest/non-forest assessment. Några praktiskt avgörande punkter:

- Man ska rapportera **typ av fjärranalysdata** (t.ex. satellit/radar), upplösning och datakällor på ett sätt som möjliggör replikering. citeturn12view0  
- Fjärranalys-scener bör vara daterade **minst 10 år före projektstart** och **vid projektstart**. citeturn12view0  
- Klassificeringsnoggrannhet: “minimum overall accuracy … 90%” (per klass), med accuracy assessment baserad på ground-truth (survey) eller högre upplöst imagery, och man ska leverera shapefile med punkterna som användes för accuracy assessment. citeturn12view0turn11view1  
- Det finns också mycket specifika regler kring moln/skuggor, där kravbilden blir konservativ och ground-truthing i vissa fall måste göras utan sampling (“sampling is not allowed” i den specificerade situationen), vilket i sin tur driver hur man planerar fältkampanjer och loggar GPS-spår. citeturn12view0  

Utöver RS-protokollet kräver LUF att projekt levererar en uppsättning **GIS-vektorlager**, bl.a. project region/area, eligible areas, modelling units, infrastruktur, vatten, skyddade områden, biodiversitetsområden samt lager kopplade till berörda människor och platser med kulturell/religiös betydelse. Detta är en direkt “dataproduktionslista” som pipeline måste kunna exportera versionssatt. citeturn13view0

LUF-guiden om osäkerhet anger dessutom att man ska nå en target precision (±20% vid 90% konfidens) för LUF-parametrar och beskriver hur on-site mätningar, litteraturdata eller defaultfaktorer får användas samt hur konservativ “uncertainty deduction” ska tillämpas om tröskeln inte uppfylls. Detta påverkar både provtagningsdesign och hur beräkningskedjan dokumenteras. citeturn13view0turn11view3

### Blue Carbon och nya nature-metoder

Blue Carbon & Freshwater Wetlands Activity Requirements kräver att man skickar in specificerade GIS-lager (tabellstyrt) och kopplar osäkerhetsbedömning till LUF-ramverket (“Annex A” i LUF), samt anger en **miniminivå för compliance buffer** (20% om inte metodik säger annat). Det här gör att pipeline bör kunna hantera marina/estuarina lager (t.ex. EEZ) och samtidigt återanvända LUF-objektmodellen för osäkerhet och stratifiering. citeturn5search3

För mangrove- och biomassa-MRV är det särskilt relevant att Gold Standard i metodiken för Sustainable Management of Mangroves uttryckligen tillåter kombination av in situ-mätningar och fjärranalys; den listar flera godtagna angreppssätt, inklusive regression mellan onsite-biomassa och RS-biomassaskattning. Det öppnar för en pipeline där fältteamets biomassaplots blir “training/validation data” till RS-modellen, och där man kan paketera både modellmetadata och ground truth som verifieringsbart underlag. citeturn5search0

### SDG Impact Tool och indikatorval

Gold Standard har egna krav för val av SDG-monitoreringsindikatorer: projekt ska visa bidrag till minst tre SDGs inklusive SDG 13, indikatorer får bara väljas från SDG Impact Tool (ingen manuell override), och indikatorer måste vara spårbara, transparenta och verifierbara samt inte leda till dubbelräkning. Det ger en tydlig regelmotor att implementera i en automatiserad pipeline. citeturn21view0

### Digital MRV och remote audit

Gold Standard driver aktivt digitalisering via Assurance Platform (integrerad med Registry) och en dMRV-pilot (till och med 30 oktober 2026). Pilotkraven betonar bland annat att projektutvecklaren ansvarar för datahantering (lagring, åtkomst, retrieval och backup), och definierar även hur monitoreringsperioder kopplas till “issuance tracks”. Det gör dMRV-piloten till en legitim referensram när man motiverar automatisering i ett GS4GG-projekt. citeturn22view0turn19search0turn20view0

Samtidigt är det viktigt att notera att Gold Standard-dokumentet om site visit och remotely audits (v2.0) uttryckligen säger att dess remote assessment-krav **inte gäller LUF-projekt** och att separat upplägg ska utvecklas för LUF. I en strategi måste detta markeras som “ospecificerat” tills relevanta LUF-specifika remote audit-regler finns eller tills man får en formell tolkning via Gold Standard. citeturn9view0

## Kravmappning till Mergin-formulär

Tabellen nedan är avsedd som ett “designkontrakt” mellan Gold Standard-krav och fältinsamlingen. Den är generell för GS4GG/LUF och måste därefter justeras per vald metodik (A/R, AGR, Blue Carbon/Mangrove etc.). citeturn3view0turn13view0turn5search3turn21view0turn8view0

| Gold Standard-krav (prioriterad klausul) | Krävt fält i Mergin-form / lager | Exempelvärde | Evidenstyp | Frekvens |
|---|---|---|---|---|
| Monitoring & Reporting Plan: för varje parameter ska metric, frekvens, metod, ansvarig och QC beskrivas citeturn3view0 | `parameter_id`, `metric_name`, `method`, `collector_org`, `qc_method`, `ethical_notes` | `SOC_0_30cm`, “g C/kg”, “jordprov + lab”, “FieldTeam A”, “dubbelprov 10%”, “samtycke krävs” | Formpost + SOP/PDF | Vid design + uppdateras vid ändring |
| Monitoring indicator selection: inga manuella indikatorer, endast SDG Impact Tool; indikatorer ska vara spårbara/verifierbara citeturn21view0 | `sdg_indicator_id`, `sdg_target`, `causal_pathway_ref`, `disaggregation_plan` | “SDG13-…”, “13.x”, “TheoryOfChange_v1”, “kön/ålder/kommun” | SDG Tool-export + bilaga | Vid design + vid design change |
| Minst 3 SDGs inkl. SDG 13 citeturn21view0 | `sdg_list[]` | `[13, 15, 6]` | SDG Tool-export | Vid design |
| Kartkrav: map metadata inkl. satellit-/flygbild datum, upplösning, datakälla citeturn4view0 | `map_id`, `crs`, `imagery_date`, `imagery_resolution`, `imagery_source` | “MAP_BASELINE_01”, “EPSG:4326”, “2014‑06‑15”, “10 m”, “Sentinel‑2 L2A” | Auto-genererad karta + metadatafil | Vid PDD + vid uppdatering |
| LUF RS-protokoll: rapportera typ av RS-data och källa så analysen kan replikeras citeturn12view0 | `rs_sensor`, `rs_resolution`, `rs_source`, `processing_software` | “Landsat 8”, “30 m”, “USGS”, “QGIS+…/skript v1” | RS-metodnot + logg | Vid design |
| LUF RS-protokoll: scener minst 10 år före start och vid startdatum citeturn12view0 | `baseline_scene_date`, `start_scene_date`, `project_start_date` | “2012‑07‑01”, “2022‑07‑01”, “2022‑08‑15” | RS-metadata | Vid design |
| LUF RS-protokoll: accuracy assessment ≥90%, shapefile med kontrollpunkter citeturn12view0 | Lager `accuracy_points` (punkter) + fält `class_ref`, `class_pred`, `source` | “forest/non-forest”, “forest”, “ground_truth” | Punktlager + confusion matrix | Vid design + vid större uppdatering |
| LUF: obligatoriska GIS-lager (project region/area, eligible areas, modelling units, vatten, skydd etc.) citeturn13view0 | Lager: `project_region`, `project_area`, `eligible_areas`, `modelling_units`, `water_bodies`, `protected_areas`, `biodiversity_areas`, `affected_people_points`, `cultural_sites` | (geometrier) | Vector layers (GPKG/shape) | Vid design + vid design change |
| Stakeholder consultation: minst två rundor inkl. fysisk meeting + 30 dagar feedback citeturn26view4turn25view0 | `sc_meeting_date`, `sc_feedback_start`, `sc_feedback_end`, `sc_attendance_list_ref` | “2026‑05‑12”, “2026‑05‑13”, “2026‑06‑12”, “ATT_01.pdf” | SC-rapport + närvarolista | Vid design |
| Kontinuerlig grievance: logga alla kommentarer, skicka mottagningsbekräftelse, återkoppla åtgärder citeturn26view0 | `grievance_id`, `channel`, `received_at`, `summary`, `ack_sent_at`, `status`, `resolution_note` | “GR‑2026‑001”, “telefon”, “2026‑08‑01”, “…”, “2026‑08‑02”, “closed”, “åtgärd X” | Grievance-logg | Löpande |
| Safeguarding: evidens ska tillhandahållas VVB och (med undantag) publiceras på Impact Registry citeturn24view1 | `safeguard_risk_id`, `principle`, `mitigation_plan_ref`, `evidence_ref`, `confidential_flag` | “P9‑HCV‑01”, “P.9”, “MIT_02.pdf”, “EIA_2026.pdf”, `true/false` | Riskregister + bilaga | Vid design + vid periodisk reassessment |
| Verifiering: audit trail måste täcka hela perioden och bygga på verifierbar evidens citeturn8view0 | `evidence_id`, `evidence_hash`, `source_system`, `time_coverage_start/end` | “EV‑123”, “sha256:…”, “Mergin+PostGIS”, “2026‑01‑01/2026‑12‑31” | Systemlogg + checksummor | Löpande |
| LUF buffer/GS buffer: 20% till Gold Standard Buffer för LUF (sequestration-delen) citeturn18view2 | `issuance_request_id`, `gsver_total`, `gsver_sequestration`, `buffer_20pct` | 10,000 / 8,000 / ¹1,600 | Issuance-beräkning + registerunderlag | Vid issuance |
| Carbon performance: stocks ska vara aligned med issued PERs/GSVERs; mall krävs citeturn18view3 | `carbon_stock_estimate`, `carbon_stock_method_ref`, `carbon_performance_template_ref` | “tCO2e=…”, “RS+plots v1”, “CP_2026.xlsx” | Carbon Performance-paket | Vid performance cert/issuance |

*Not: där Gold Standard har metodikspecifika krav (t.ex. provtagningsdesign, SOC-pooler, biomassaekvationer) måste tabellen kompletteras med exakt metodiktext; vid oklarhet markeras klausulen som “ospecificerad” i projektets kontrollista tills formell tolkning finns.* citeturn20view0turn9view0turn12view0

## Föreslagen arkitektur för Mergin Maps → automatiserad MRV-pipeline

Mergin Maps är i grunden fil- och versionsbaserat (GeoPackage i projektet) och har en etablerad tvåvägssynk för att koppla till PostGIS (DB Sync). Det gör att du kan använda PostGIS som analytisk “source of truth” utan att tvinga fältteamet att jobba direkt mot databasanslutningar. citeturn31search0turn31search6

En nyckelfråga i praktiken är: **måste QGIS-projektet vara igång hela tiden?** Nej: synkningen sker mellan klient (mobil/desktop) och Mergin-servern. QGIS används för projektförberedelse/stil/formlogik, men behöver inte vara uppe för att fältteam ska synka. Däremot behöver DB Sync (om du vill ha “nära realtid” mellan Mergin GeoPackage och PostGIS) köras som en tjänst/daemon eller schemalagt jobb, eftersom det är komponenten som automatiskt pushar förändringar mellan systemen. citeturn30search0turn31search0turn31search6

### Arkitekturflöde

```mermaid
flowchart TD
  A[Fältteam i Mergin Maps\nformulär + GPS + foto] --> B[Mergin Maps Server\nCloud/EE/CE]
  B --> C[Projektdata som GeoPackage\n+ versionshistorik]
  B --> D[Media/attachments\nfoton, PDF, ljud]
  
  %% Data storage options
  C --> E[DB Sync\n(GPKG <-> PostGIS)]
  E --> F[PostGIS\nMRV-schema]
  
  %% Event-driven automation
  F --> G[Event-trigger\nLISTEN/NOTIFY eller Logical Decoding]
  G --> H[Worker/Orkestrering\nQA + regelkontroller + rapportbygge]
  
  %% Compliance reasoning
  H --> I[Gemini-stöd\nklausulcheck + avvikelser + textutkast]
  I --> H
  
  %% Remote sensing / spatial analytics
  H --> J[Fjärranalys & GIS-beräkningar\nklassificering, arealer, osäkerhet]
  J --> F
  
  %% Human review points
  H --> K[Mänsklig granskning\nGIS/QA/Juridik]
  K --> H
  
  %% Outputs
  H --> L[Audit evidence pack\nhashar, loggar, bilagor, export]
  L --> M[Gold Standard Assurance Platform/Registry\ninlämning (manuell upload)]
```

Den händelsedrivna delen kan göras på två nivåer:

- **LISTEN/NOTIFY** när nya/uppdaterade observationer skrivs till PostGIS (snabbt, enkelt, “good enough” för många pilots), där en payload kan skickas med och worker hämtar det fulla underlaget från databasen. citeturn32search3turn32search15  
- **Logical Decoding (CDC)** om du vill bygga en “audit log” som fångar alla persistenta ändringar robust och i rätt ordning, direkt från WAL. Detta passar särskilt om du vill kunna rekonstruera vad som ändrades när, av vem och via vilken process, utan att lita på applikationsloggar. citeturn32search2turn32search6  

### Var Gemini passar in utan att riskera revisionen

Gold Standard kräver att indikatorer, evidens och audit trail är spårbara och verifierbara, och att VVB bara certifierar baserat på verifierbar evidens. Därför ska Gemini inte vara ett “beslutsorgan” utan:

- en “kontrollmotor” som mappar inkommande dataposter mot ett klausul-bibliotek (t.ex. 101 P&R + relevanta AR/metodiker) och returnerar “pass/flagga/kräver mänsklig tolkning”, samt genererar en *klausulrefererad* motivering (med citat/klausul-ID) som sedan signeras av en mänsklig reviewer, citeturn8view0turn21view0turn3view0  
- en texthjälp som producerar utkast till Monitoring Report-avsnitt, stakeholder/grievance-sammanställningar och method statement för RS-klassificering, där alla output kopplas till underliggande evidens-ID:n (inte “modellens minne”). citeturn4view0turn26view0turn12view0  

Gold Standard beskriver i remote audit-dokumentet att ICT kan inkludera bl.a. AI, drönare, video etc. Det kan användas för att samla, överföra och bedöma evidens, men auditkraven kvarstår och måste dokumenteras i VVB-rapportering. citeturn9view0turn7view5  

image_group{"layout":"carousel","aspect_ratio":"16:9","query":["Mergin Maps mobile app field data collection","Mergin Maps QGIS plugin","PostGIS database logo","Gold Standard for the Global Goals logo"],"num_per_query":1}

## Datamodell och spårbarhet

### Enkel ER-tabell för MRV-datamodell i PostGIS

Syftet med datamodellen är att göra varje påstående i Monitoring Report spårbart till (a) rådata i fält, (b) bilagor, (c) beräkningskedja och (d) revisionslogg—i linje med kravet på audit trail och verifierbar evidens. citeturn8view0turn3view0  

| Tabell | Primärnyckel | Viktiga fält | Relationer | Kommentar om audit trail |
|---|---|---|---|---|
| `project` | `project_id` | `gs_project_name`, `host_country`, `methodology_id`, `start_date` | 1–M mot alla | Bär GS-ID och metodikval |
| `project_area` | `area_id` | `geom`, `crs`, `area_type` | M–1 `project` | Versionssätts; används för “boundary/area” |
| `eligible_area` | `eligible_id` | `geom`, `eligibility_basis` | M–1 `project` | Kopplar direkt till LUF Annex C-resultat citeturn12view0 |
| `modelling_unit` | `mu_id` | `geom`, `stratum`, `land_use` | M–1 `project` | Krävs i LUF GIS-lager citeturn13view0 |
| `observation` | `obs_id` | `geom`, `obs_type`, `obs_value`, `unit`, `obs_time`, `collector_id` | M–1 `project`, M–1 `collector` | Råfältdata (ground truth, SOC, biomassaplot etc.) |
| `media_asset` | `media_id` | `file_uri`, `sha256`, `captured_at`, `device_id` | M–1 `observation` (valfritt) | Hash + metadata för verifierbarhet citeturn8view0 |
| `rs_scene` | `scene_id` | `sensor`, `scene_date`, `resolution`, `source`, `download_ref` | M–1 `project` | Uppfyller RS metadata-krav citeturn12view0 |
| `classification_run` | `run_id` | `method`, `software_version`, `parameters_json`, `output_raster_ref` | M–1 `project`, M–M `rs_scene` | Reproducerbarhet + “method statement” citeturn12view0 |
| `accuracy_point` | `pt_id` | `geom`, `class_ref`, `class_pred`, `source` | M–1 `classification_run` | Exporteras som shapefile enligt LUF citeturn12view0 |
| `grievance` | `grievance_id` | `channel`, `received_at`, `summary`, `ack_at`, `status` | M–1 `project` | Krav på loggning/återkoppling citeturn26view0turn24view3 |
| `safeguard_risk` | `risk_id` | `principle`, `risk_level`, `mitigation_ref`, `evidence_ref` | M–1 `project` | Evidens ska kunna publiceras (med undantag) citeturn24view1 |
| `qa_check` | `qa_id` | `check_type`, `result`, `reviewer`, `reviewed_at`, `notes` | M–1 `observation`/`run` | Mänskliga “sign-offs” |
| `audit_event_log` | `event_id` | `source`, `event_time`, `payload`, `actor` | M–1 `project` | Kan fyllas via LISTEN/NOTIFY eller CDC citeturn32search3turn32search2 |

### Kedja av bevis och “public vs confidential”

Gold Standard kräver att projekt­dokumentation (förutom konfidentiell info) görs publikt tillgänglig via Impact Registry, och att safeguarding-stödjande dokument/evidens i princip också ska göras publika med undantag för konfidentialitet. Därför måste systemet skilja på (1) publika bilagor och (2) känslig data (t.ex. personuppgifter i grievance/attendancelistor), med tydliga redaktionsrutiner innan uppladdning. citeturn4view0turn24view1

Det är även direkt kopplat till stakeholder-kraven: man ska kunna visa att man registrerat kommentarer, gett återkoppling, och rapporterat concerns i annual/monitoring reporting. En datamodell som binder grievance → åtgärd → rapportavsnitt gör detta mycket enklare vid audit. citeturn26view0turn3view0

## Genomförandeplan, risker och auditpaket

### Prioriterad dokumentlista med klausuler och korta citat

Nedan är en rekommenderad läsordning (högst “bärighet” först) för att bygga MRV-kontroller, formulär och rapportmallar. Citat är korta och bör kopieras med klausulreferens i er interna compliance-matris.

1) **Principles & Requirements v2.1** (Monitoring Plan + kartmetadata + projektdokumentation). Exempelcitat: “For each monitored parameter… frequency… method… quality control…” (krav på planens innehåll). citeturn3view0turn4view0  

2) **Validation and Verification Standard v2.0** (audit trail). Exempelcitat: “confirm that there is an audit trail that contains the evidence and records…” citeturn8view0  

3) **LUF Activity Requirements v1.2.1** (GIS-lager, RS-protokoll, accuracy ≥90%, scen-datum). Exempelcitat: “Remote sensing scenes should be dated… at least 10 years before…” citeturn12view0  

4) **Safeguarding Principles & Requirements v2.1** (evidenskrav, publicering, grievance). Exempelcitat: “evidence… shall be provided… The supporting documents and evidence shall be made publicly available…” citeturn24view1  

5) **Stakeholder Consultation & Engagement Requirements v2.1** (två rundor + löpande grievance). Exempelcitat: “record all comments… [and] send a written acknowledgement…” citeturn26view0  

6) **Requirements for Monitoring Indicator Selection in SDG Impact Tool v1.0** (indikatorregler). Exempelcitat: “Manual entry or override… is strictly prohibited.” citeturn21view0  

7) **GHG Emissions Reductions & Sequestration Product Requirements v3.2** (LUF buffer, carbon performance, double counting). Exempelcitat: “20%… transferred into the Gold Standard Buffer.” citeturn18view2turn18view3  

8) **dMRV pilot requirements (pilot v0.1)** (data management ansvar). Exempelcitat: projektutvecklaren ansvarar för “data storage, access, retrieval, and backup.” citeturn20view0  

9) **Blue Carbon & Freshwater Wetlands AR v1.0** (GIS-lager + osäkerhet + buffer). citeturn5search3  

10) **Mangrove Methodology v1.0** (RS + fältkombination för biomassa). citeturn5search0  

### Länksamling till primärkällor

```text
Gold Standard (GS4GG) – Principles & Requirements v2.1 (PDF)
https://globalgoals.goldstandard.org/standards/101_V2.1_PAR_Principles-Requirements.pdf

Validation and Verification Standard v2.0 (PDF)
https://globalgoals.goldstandard.org/standards/113_V2.0_PAR_Validation-and-Verification-Standard.pdf

Land Use & Forests Activity Requirements v1.2.1 (PDF)
https://globalgoals.goldstandard.org/standards/203_V1.2.1_AR_LUF-Activity-Requirements.pdf

Safeguarding Principles & Requirements v2.1 (PDF)
https://globalgoals.goldstandard.org/standards/103_V2.1_PAR_Safeguarding-Principles-Requirements.pdf

Stakeholder Consultation & Engagement Requirements v2.1 (PDF)
https://globalgoals.goldstandard.org/standards/102_V2.1_PAR_Stakeholder-Consultation-Requirements.pdf

Requirements for Monitoring Indicator Selection in SDG Impact Tool v1.0 (PDF)
https://globalgoals.goldstandard.org/standards/118_V1.0_PAR_Requirements-for-Monitoring-Indicator-Selection.pdf

GHG ER & Sequestration Product Requirements v3.2 (PDF)
https://globalgoals.goldstandard.org/standards/501_V3.2_PR_GHG-Emissions-Reductions-Sequestration.pdf

Blue Carbon & Freshwater Wetlands Activity Requirements v1.0 (PDF)
https://globalgoals.goldstandard.org/standards/204_V1.0_AR_BCFW_Blue-Carbon-and-Freshwater-Wetlands-Activity-Requirements.pdf

Methodology for Sustainable Management of Mangroves v1.0 (PDF)
https://globalgoals.goldstandard.org/standards/443_V1.0_BCFW_Sustainable-Management-of-Mangroves.pdf

dMRV Pilot Programme page
https://globalgoals.goldstandard.org/digital-measurement-reporting-verification-pilot-programme/

dMRV Programme Requirements (Pilot 0.1) (PDF)
https://globalgoals.goldstandard.org/standards/DMRV-Programme-DMRV-Requirements-pilot-v0.1.pdf

Mergin Maps DB Sync docs
https://merginmaps.com/docs/dev/dbsync/

Mergin Maps Python API client docs
https://merginmaps.com/docs/dev/integration/

OGC GeoPackage standard
https://www.ogc.org/standards/geopackage/
https://www.geopackage.org/spec/

PostgreSQL LISTEN/NOTIFY + Logical Decoding docs
https://www.postgresql.org/docs/current/libpq-notify.html
https://www.postgresql.org/docs/current/logicaldecoding-explanation.html
```

*Ryska versioner:* i den här genomgången hittades inga officiella ryska översättningar av kärnstandarderna på globalgoals.goldstandard.org; utgå från engelska som primär text och flagga behov av lokalspråk som en “ospecificerad” punkt att förankra med Gold Standard/VVB. citeturn4view0  

### Implementation plan med milstolpar

**Minimal pilot** (ca 6–10 veckor, grovt):  
Pilotens mål är att bevisa att ni kan skapa en end-to-end evidenskedja som matchar (i) Monitoring Plan-krav, (ii) LUF GIS/RS-underlag och (iii) audit trail-krav, men utan full skala på alla SDG-indikatorer.

- Vecka 1–2: “Compliance blueprint”. Välj metodikspår (t.ex. LUF A/R eller AGR eller Blue Carbon) och skapa en klausulmatris + datakatalog, inkl. “vad måste vara publikt” vs konfidentiellt. citeturn3view0turn13view0turn24view1turn8view0  
- Vecka 2–4: Bygg Mergin-projektpaket: GeoPackage-schema/lager, formulär, obligatoriska fält, constraints, samt “evidence-ID”-konvention (t.ex. auto-ID för foton/figurer). citeturn4view0turn13view0  
- Vecka 4–6: Sätt upp DB Sync och MRV-schema i PostGIS. Etablera en första event-trigger (LISTEN/NOTIFY) och worker som kör: fältvalidering + geometri-/topologikontroller + export av GIS-lager. citeturn31search0turn32search3  
- Vecka 6–8: Lägg till RS-modul (minst Annex C-krav: scen-datum, metadata, accuracy-punkter) och generera första “audit evidence pack”. citeturn12view0turn8view0  
- Vecka 8–10: Gemini-stöd i “read-only mode” (flagga/utkast), samt definiera mänskliga sign-off punkter. citeturn9view0turn8view0  

**Produktion** (ytterligare ca 3–6 månader, grovt):  
Här adderar man CDC-loggning (logical decoding), mer avancerad osäkerhetsmodul (LUF Annex A), full incident/grievance-rapportering och färdiga rapportmallar för issuance/performance certification. citeturn13view0turn32search2turn18view3turn26view0  

**Roller** (minimalt team):  
En GIS/RS-ansvarig (metodik + spatial logik), en backendutvecklare (PostGIS + worker + integration), en QA/data steward (data governance + test + evidenspaket), samt en juridisk/standards-granskare (host country-regler, dubbelräkning, sekretess/publicering). Roller och ansvar harmonierar med Gold Standards dMRV-pilotkrav som lägger data management ansvar på projektutvecklaren och revisionsansvar på VVB. citeturn20view0turn8view0  

### Risker och mitigering

**Datakvalitet (fält)**: risk för inkonsekventa attribut, fel geometri, eller “orphan media”. Mitigering: constraints i formulär, obligatoriska metadatafält (metod, tid, ansvarig), och automatisk QA som returnerar avvisning/återkoppling innan data går vidare till “MRV-ready”. citeturn3view0turn8view0  

**Auditabilitet och chain of custody**: risk att man inte kan visa full tidsmässig täckning (evidence gaps) eller korscheck. Mitigering: audit trail-tabell + checksummor + periodiska “coverage reports” som VVB kan följa, i linje med kravet på evidensens frekvens/täckning och korscheck. citeturn8view0  

**Remote audit-ambiguitet för LUF**: eftersom remote audit-dokumentet (v2.0) inte gäller LUF, finns risk att man antar fel. Mitigering: behandla remote audit för LUF som “ospecificerat” och designa systemet så att fysisk site visit fortfarande kan stödjas fullt ut (printbara checklistor, GPS-spår, fotobevis, intervjuunderlag), samt följ upp med Gold Standard/VVB. citeturn9view0turn20view0  

**AI-fel (Gemini)**: risk för hallucinationer, felaktig klausultolkning eller missad avvikelse. Mitigering: (1) lås Gemini till retrieval-baserade klausulutdrag, (2) kräva mänsklig sign-off för alla compliance-utlåtanden, (3) logga prompts/inputs/outputs som intern QA-artefakt men inte som primär evidens. Detta är i linje med att verifiering ska baseras på verifierbar evidens snarare än modellpåståenden. citeturn8view0turn9view0  

**Sekretess vs publik transparens**: risk att persondata hamnar i publika bilagor. Mitigering: “public/confidential”-flagga per evidensobjekt, och en obligatorisk redaktionsprocess innan uppladdning, eftersom standarderna kräver publik tillgänglighet med undantag för konfidentiell information. citeturn4view0turn24view1  

### Exempelmallar

**Fältformulärschema (exempel, konceptuellt)**  
*(Anpassas per metodik och indikator. Poängen är att alltid bära QC + metodmetadata per mätning.)* citeturn3view0turn21view0  

```yaml
layer: observation
geometry: Point
fields:
  - name: obs_id
    type: uuid
    required: true
  - name: project_id
    type: uuid
    required: true
  - name: obs_type
    type: enum
    values: [ground_truth, soil_sample, biomass_plot, stakeholder_interview, grievance_entry]
    required: true
  - name: obs_time
    type: datetime
    required: true
  - name: obs_value
    type: numeric_or_text
    required: true
  - name: unit
    type: text
    required_if: obs_type in [soil_sample, biomass_plot]
  - name: method
    type: text
    required: true
  - name: collector_org
    type: text
    required: true
  - name: qc_method
    type: text
    required: true
  - name: evidence_id
    type: text
    required: true
  - name: ethics_notes
    type: text
    required: false
attachments:
  - photos:
      store_as: media_asset
      require_hashing: true
```

**Automatiserat rapportutdrag (Monitoring Report – audit-ready “evidence index”)** citeturn8view0turn4view0  

```text
EVIDENCE INDEX – Monitoring Period: 2026-01-01 to 2026-12-31

1. Data sources
   - Mergin project: <name>, version range: v120–v188
   - PostGIS schema: mrv_prod
   - Remote sensing scenes: scene_id list + metadata (sensor/date/resolution/source)

2. Audit trail coverage
   - Coverage check: PASS (evidence spans full monitoring period)
   - Cross-check sources used: plant logs / surveys / database extracts (as applicable)

3. Evidence objects
   - EV-000132: soil_sample at POINT(...), 2026-03-12, lab_report.pdf (sha256:...)
   - EV-000201: ground_truth point set for RS accuracy (shapefile export + confusion matrix)
   - EV-000305: grievance GR-2026-001 summary + acknowledgement record
```

**Grievance/verification package (för VVB och Gold Standard review)** citeturn26view0turn24view3turn8view0  

```text
PACKAGE: Verification Support – Period YYYY

A) Grievance log export (anonymised where needed)
   - All entries with timestamps, channel, status, acknowledgement timestamp

B) Safeguarding evidence bundle
   - Risk register + mitigation evidence references (public/confidential flags)

C) Spatial deliverables
   - Project region/area/eligible areas/modelling units + required layers (GPKG + PDF map layout w/ metadata)

D) Remote sensing documentation
   - Scene list (10 years before + start date), processing method, accuracy assessment points + results

E) Audit trail + change summary
   - Event log extracts + hash list for attachments
```

### Compliance-checklista inför audit

Den här checklistan är formulerad för att vara “torrt reviderbar”: varje punkt ska kunna besvaras med (Ja/Nej + evidens-ID). citeturn8view0turn3view0turn12view0turn21view0turn26view0turn24view1  

- Monitoring & Reporting Plan innehåller för varje parameter: metric, frekvens, insamlingsmetod, ansvariga och QC.  
- SDG-indikatorer är valda enligt SDG Impact Tool-regler (inga manuella indikatorer), är relevanta och inte dubbelräknade.  
- GIS-lager enligt relevant Activity Requirements är exporterade och versionssatta.  
- LUF: RS-scener och metadata uppfyller datumkraven; accuracy assessment visar minst 90% (där kravet gäller) och punkter kan levereras som shapefile.  
- Stakeholder: två konsultationsrundor dokumenterade; continuous grievance fungerar, loggas och återkopplas.  
- Safeguarding: evidens finns tillgänglig för VVB; public/confidential hanteras.  
- Audit trail: evidens täcker hela perioden; korscheck-källor är identifierade; alla siffror i rapport kan spåras till rådata och bilagor.  
- (LUF/remote audit) Om remote audit används: behandla som “ospecificerat” och dokumentera uttryckligen hur fysisk/verifierbar kontroll säkerställs i frånvaro av LUF-specifika remote audit-krav.