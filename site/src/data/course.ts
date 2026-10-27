/**
 * The course, read straight from the repository's own source of truth.
 *
 * `course/lessons/*.md` is the source of truth for the lessons (the rule in
 * course/FORMAT.md). `course/curriculum.json` is generated from those files by
 * `python tools/course_check.py --index`, and the gate fails the build if the
 * two disagree - so reading the generated index here means the site cannot
 * drift from the course in the repo.
 *
 * The lesson bodies are imported as Astro markdown, so the site renders the
 * exact file the learner will read in the repository, not a copy of it.
 */
import curriculum from '../../../course/curriculum.json';

export interface Lesson {
  id: string;
  title: string;
  minutes: number;
  order?: number;
  concepts: string[];
  prereqs: string[];
  paths: string[];
  exercise_file: string;
  quiz: string;
  file: string;
  phase: number;
  phaseTitle: string;
  /** The Astro markdown component for the lesson body. */
  Content: unknown;
}

export interface QuizQuestion {
  id: string;
  concept: string;
  prompt: string;
  options: string[];
  answer: number;
  explain: string;
}

export interface Quiz {
  lesson_id: string;
  title: string;
  questions: QuizQuestion[];
}

// The markdown modules, eagerly loaded. Each exposes `frontmatter` and the
// compiled component as `default`. The glob is relative to this file, so
// '../../../' is the repository root.
const LESSON_MODULES = import.meta.glob<{ frontmatter: { id: string } }>(
  '../../../course/lessons/*.md',
  { eager: true },
);

const QUIZ_MODULES = import.meta.glob<Quiz>('../../../course/quizzes/*.json', {
  eager: true,
});

/**
 * The lesson files' raw text, so the page can list the lesson's own sections.
 * A lesson file is named `<id>-<slug>.md`, so the id is the front of the name.
 */
const LESSON_RAW = import.meta.glob<string>('../../../course/lessons/*.md', {
  query: '?raw',
  import: 'default',
  eager: true,
});

/**
 * The `##` sections of a lesson, in order, as [title, anchor] pairs.
 *
 * The anchor must match the id the markdown renderer puts on the heading, or
 * the rail's links land on nothing. The renderer uses the GitHub slug
 * algorithm: lowercase, drop punctuation, spaces become dashes. This mirrors
 * it - the same rule, with the same exceptions, so the two agree.
 */
function slugify(title: string): string {
  return title
    .toLowerCase()
    // The punctuation the slugger drops, rather than turning into dashes.
    .replace(/['!"#$%&()*+,./:;<=>?@[\]^`{|}~]/g, '')
    .replace(/[^\w\- ]+/g, '')
    .trim()
    .replace(/\s+/g, '-');
}

const SECTIONS = new Map<string, { title: string; anchor: string }[]>();
for (const [path, raw] of Object.entries(LESSON_RAW)) {
  const id = path.split('/').pop()?.match(/^([A-Z]\d+)/)?.[1];
  if (!id) continue;
  const sections = raw
    .split('\n')
    .filter((line) => line.startsWith('## '))
    .map((line) => {
      const title = line.slice(3).trim();
      return { title, anchor: slugify(title) };
    });
  SECTIONS.set(id, sections);
}

/** Keyed by the lesson's own id, not by its path, so a rename cannot desync it. */
const LESSON_CONTENT = new Map<string, unknown>();
for (const mod of Object.values(LESSON_MODULES)) {
  LESSON_CONTENT.set(mod.frontmatter.id, mod.default);
}

const QUIZZES: Record<string, Quiz> = {};
for (const mod of Object.values(QUIZ_MODULES)) {
  QUIZZES[mod.lesson_id] = mod;
}

export const LESSONS: Lesson[] = curriculum.phases.flatMap((phase) =>
  phase.lessons.map((lesson) => {
    const Content = LESSON_CONTENT.get(lesson.id);
    if (!Content) {
      throw new Error(
        `lesson ${lesson.id} is in the curriculum but its markdown file was not loaded. ` +
          `Run \`python tools/course_check.py --index\` if the lesson files moved.`,
      );
    }
    return {
      ...lesson,
      phase: phase.id,
      phaseTitle: phase.title,
      Content,
    } as Lesson;
  }),
);

export const LESSON_BY_ID = new Map(LESSONS.map((l) => [l.id, l]));

export const PHASES = curriculum.phases.map((phase) => ({
  id: phase.id,
  title: phase.title,
  lessons: phase.lessons.map((l) => LESSON_BY_ID.get(l.id)!),
  minutes: phase.lessons.reduce((sum, l) => sum + l.minutes, 0),
}));

export const PATHS = curriculum.paths.map((path) => ({
  id: path.id,
  label: path.label,
  lessons: path.lessons.map((id) => LESSON_BY_ID.get(id)!).filter(Boolean),
}));

export const TOTAL_LESSONS = curriculum.total_lessons;

export function quizFor(lessonId: string): Quiz | undefined {
  return QUIZZES[lessonId];
}

/** The lesson's own sections, for the on-page contents rail. */
export function sectionsFor(lessonId: string): { title: string; anchor: string }[] {
  return SECTIONS.get(lessonId) ?? [];
}

/** The next lesson in the beginner path - the order a newcomer walks. */
export function nextInPath(lessonId: string, pathId = 'beginner'): Lesson | undefined {
  const path = PATHS.find((p) => p.id === pathId);
  if (!path) return undefined;
  const index = path.lessons.findIndex((l) => l.id === lessonId);
  return index >= 0 ? path.lessons[index + 1] : undefined;
}

export function prevInPath(lessonId: string, pathId = 'beginner'): Lesson | undefined {
  const path = PATHS.find((p) => p.id === pathId);
  if (!path) return undefined;
  const index = path.lessons.findIndex((l) => l.id === lessonId);
  return index > 0 ? path.lessons[index - 1] : undefined;
}

/** The lesson a newcomer should read first. */
export const FIRST_LESSON = PATHS.find((p) => p.id === 'beginner')?.lessons[0];
