import {
  BarChart,
  Callout,
  Code,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  Link,
  Pill,
  Row,
  Stack,
  Stat,
  Table,
  Text,
  useCanvasState,
} from "cursor/canvas";

type CandidateId = "tobi" | "kaggle" | "bitext";

const CANDIDATES: Record<
  CandidateId,
  {
    name: string;
    sourceLabel: string;
    sourceUrl: string;
    version: string;
    license: string;
    licenseNote: string;
    ticketText: string;
    routingLabel: string;
    optional: string;
    english: string;
    englishCount: number;
    fit: string;
  }
> = {
  tobi: {
    name: "Customer Support Tickets (Tobi-Bueck / Softoft)",
    sourceLabel: "Hugging Face dataset card",
    sourceUrl: "https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets",
    version:
      "Revision ddf1c81 · last modified 2026-06-28 · DOI 10.57967/hf/6184",
    license: "CC BY-NC 4.0",
    licenseNote:
      "Public download. Educational analysis allowed. Commercial use prohibited. Attribution required.",
    ticketText: "subject + body",
    routingLabel: "queue (department / support team)",
    optional: "priority, type, language, tags, agent answer",
    english: "28,261 of 61,765 (language = en)",
    englishCount: 28261,
    fit: "Closest to the target use case: each record is a support email with text available at arrival and a queue that names the team.",
  },
  kaggle: {
    name: "IT Service Ticket Classification Dataset",
    sourceLabel: "Kaggle listing",
    sourceUrl:
      "https://www.kaggle.com/datasets/adisongoh/it-service-ticket-classification-dataset",
    version:
      "File all_tickets_processed_improved_v3.csv · listing last updated ~2023",
    license: "CC0: Public Domain",
    licenseNote:
      "Educational analysis allowed. A free Kaggle account is typically required to download.",
    ticketText: "Document",
    routingLabel: "Topic_group (8 IT categories)",
    optional: "None in this file",
    english: "47,837 (English IT tickets; no language column)",
    englishCount: 47837,
    fit: "Eligible and large, but pre-cleaned text-and-label only. No priority, channel, or other arrival metadata.",
  },
  bitext: {
    name: "Bitext Customer Service Tagged Training Dataset",
    sourceLabel: "Hugging Face dataset card",
    sourceUrl:
      "https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset",
    version:
      "File …_27K_responses-v11.csv · listing last modified 2024-07-18",
    license: "CDLA-Sharing-1.0",
    licenseNote:
      "Public download. Educational analysis allowed. Redistribution of the data must remain under CDLA-Sharing-1.0.",
    ticketText: "instruction (user request)",
    routingLabel: "category (10 groups); finer intent (27 classes)",
    optional: "flags, example response",
    english: "26,872 (English-only)",
    englishCount: 26872,
    fit: "Eligible labels, but records are synthetic chatbot utterances rather than full support tickets.",
  },
};

export default function Task1DatasetSelection() {
  const [selected, setSelected] = useCanvasState<CandidateId>(
    "candidate-tab",
    "tobi",
  );
  const detail = CANDIDATES[selected];

  return (
    <Stack gap={20}>
      <Stack gap={6}>
        <H1>Task 1 — Find and select a dataset</H1>
        <Text tone="secondary">
          Intended use: given the text of a newly arrived support ticket, route
          it to the appropriate support team. Retrieved 2026-09-28.
        </Text>
      </Stack>

      <Callout tone="success" title="Selected: Customer Support Tickets">
        Tobi-Bueck / Softoft is the closest match. Each record is a support
        email with arrival text (`subject`, `body`) and a categorical routing
        target (`queue`) that names the support team. It also has priority,
        type, tags, and language, plus 28,261 English examples. The Kaggle set
        is cleaned text-and-label only; Bitext is synthetic chatbot utterances,
        not full tickets.
      </Callout>

      <Row gap={24} wrap>
        <Stat value="3" label="Public candidates" />
        <Stat value="28,261" label="English tickets in selected set" tone="info" />
        <Stat value="CC BY-NC 4.0" label="Selected license (edu. OK)" />
      </Row>

      <Stack gap={8}>
        <H2>Candidate comparison</H2>
        <Text size="small" tone="tertiary">
          Source: dataset cards and listings, retrieved 2026-09-28. None of the
          three licenses prohibit educational analysis.
        </Text>
        <Table
          striped
          stickyHeader
          rowTone={["success", "neutral", "neutral"]}
          headers={[
            "Dataset",
            "License",
            "Ticket text",
            "Routing label",
            "Optional context",
            "English records",
          ]}
          rows={[
            [
              "Customer Support Tickets (selected)",
              "CC BY-NC 4.0",
              "subject + body",
              "queue",
              "priority, type, tags, language, answer",
              "28,261 / 61,765",
            ],
            [
              "IT Service Ticket Classification",
              "CC0",
              "Document",
              "Topic_group",
              "None in this file",
              "47,837",
            ],
            [
              "Bitext Customer Service",
              "CDLA-Sharing-1.0",
              "instruction",
              "category / intent",
              "flags, response",
              "26,872",
            ],
          ]}
        />
      </Stack>

      <Stack gap={8}>
        <H2>Usable English records by candidate</H2>
        <BarChart
          horizontal
          height={180}
          categories={[
            "Tobi-Bueck (selected)",
            "Kaggle IT tickets",
            "Bitext",
          ]}
          series={[
            {
              name: "English records",
              data: [28261, 47837, 26872],
              tone: "info",
            },
          ]}
          showValues
        />
        <Text size="small" tone="tertiary">
          Count of usable English records. Tobi-Bueck English count is
          language=en in the combined Hugging Face parquet snapshot (61,765
          total). Kaggle has no language column. Bitext is English-only.
        </Text>
      </Stack>

      <Divider />

      <Stack gap={10}>
        <H2>Candidate details</H2>
        <Row gap={8} wrap>
          <Pill active={selected === "tobi"} onClick={() => setSelected("tobi")}>
            Tobi-Bueck (selected)
          </Pill>
          <Pill
            active={selected === "kaggle"}
            onClick={() => setSelected("kaggle")}
          >
            Kaggle IT tickets
          </Pill>
          <Pill
            active={selected === "bitext"}
            onClick={() => setSelected("bitext")}
          >
            Bitext
          </Pill>
        </Row>

        <H3>{detail.name}</H3>
        <Text>
          Source: <Link href={detail.sourceUrl}>{detail.sourceLabel}</Link>
        </Text>
        <Grid columns={2} gap={16}>
          <Stack gap={4}>
            <Text size="small" tone="tertiary">
              Version
            </Text>
            <Text>{detail.version}</Text>
          </Stack>
          <Stack gap={4}>
            <Text size="small" tone="tertiary">
              Usage terms
            </Text>
            <Text>
              <Text weight="semibold">{detail.license}.</Text> {detail.licenseNote}
            </Text>
          </Stack>
          <Stack gap={4}>
            <Text size="small" tone="tertiary">
              Ticket text
            </Text>
            <Text>
              <Code>{detail.ticketText}</Code>
            </Text>
          </Stack>
          <Stack gap={4}>
            <Text size="small" tone="tertiary">
              Routing label
            </Text>
            <Text>
              <Code>{detail.routingLabel}</Code>
            </Text>
          </Stack>
          <Stack gap={4}>
            <Text size="small" tone="tertiary">
              Optional context
            </Text>
            <Text>{detail.optional}</Text>
          </Stack>
          <Stack gap={4}>
            <Text size="small" tone="tertiary">
              Usable English records
            </Text>
            <Text>{detail.english}</Text>
          </Stack>
        </Grid>
        <Text tone="secondary">{detail.fit}</Text>
      </Stack>
    </Stack>
  );
}
