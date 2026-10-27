/**
 * The friction field - real committed data.
 *
 * Source: runs/20261025-005353-friction-mock.json (committed to the repo).
 * Every number below is copied from that file. The run used the offline
 * simulator, so the values are the harness reproducing the SHAPE of a
 * published finding. They are never evidence about a real model, and the
 * page says so on the plot's own face.
 */

export type Projection = 'prose' | 'flat' | 'nested';

export interface FrictionRow {
  caseId: string;
  question: string;
  kind: 'noul' | 'choice' | 'score';
  values: Record<Projection, number>;
  spread: number;
  flips: boolean;
}

/** The nine measurements, in the order the harness recorded them. */
export const FRICTION_ROWS: FrictionRow[] = [
  {
    caseId: 'fmt-001-refund',
    question: 'is_urgent',
    kind: 'noul',
    values: { prose: 0.9271, flat: 0.3278, nested: 0.0 },
    spread: 0.9271,
    flips: true,
  },
  {
    caseId: 'fmt-001-refund',
    question: 'is_refund',
    kind: 'noul',
    values: { prose: 0.7043, flat: 0.4471, nested: 0.0 },
    spread: 0.7043,
    flips: true,
  },
  {
    caseId: 'fmt-001-refund',
    question: 'team',
    kind: 'choice',
    values: { prose: 0.4545, flat: 0.4545, nested: 0.4545 },
    spread: 0.0,
    flips: false,
  },
  {
    caseId: 'fmt-002-outage',
    question: 'is_urgent',
    kind: 'noul',
    values: { prose: 0.0841, flat: 0.2895, nested: 0.0 },
    spread: 0.2895,
    flips: false,
  },
  {
    caseId: 'fmt-002-outage',
    question: 'is_outage',
    kind: 'noul',
    values: { prose: 0.7485, flat: 0.0418, nested: 0.0 },
    spread: 0.7485,
    flips: true,
  },
  {
    caseId: 'fmt-002-outage',
    question: 'severity',
    kind: 'score',
    values: { prose: 0.9, flat: 0.9, nested: 0.9 },
    spread: 0.0,
    flips: false,
  },
  {
    caseId: 'fmt-003-sales',
    question: 'is_urgent',
    kind: 'noul',
    values: { prose: 0.4434, flat: 0.24, nested: 0.0 },
    spread: 0.4434,
    flips: false,
  },
  {
    caseId: 'fmt-003-sales',
    question: 'is_sales',
    kind: 'noul',
    values: { prose: 0.2377, flat: 0.6669, nested: 0.0 },
    spread: 0.6669,
    flips: true,
  },
  {
    caseId: 'fmt-003-sales',
    question: 'severity',
    kind: 'score',
    values: { prose: 0.9, flat: 0.9, nested: 0.9 },
    spread: 0.0,
    flips: false,
  },
];

/** The run file every number on the plot came from. */
export const RUN_ID = '20261025-005353-friction-mock';
export const RUN_PROVIDER = 'mock';
export const MEAN_SPREAD = 0.42;
export const MAX_SPREAD = 0.9271;
export const FLIPS_AT_HALF = 4;
export const QUESTIONS_MEASURED = 9;
export const CASES = 3;

export const PROJECTION_LABELS: Record<Projection, string> = {
  prose: 'prose',
  flat: 'flat json',
  nested: 'nested json',
};

export const PROJECTION_NOTES: Record<Projection, string> = {
  prose: 'the ticket as one paragraph of English',
  flat: 'the same ticket as flat key-value json',
  nested: 'the same ticket as nested json',
};

/** The case used in the readout: the one with the largest swing. */
export const FEATURED_CASE = 'fmt-001-refund';
export const FEATURED_QUESTION = 'is_urgent';
