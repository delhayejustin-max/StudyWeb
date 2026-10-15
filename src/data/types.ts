export type Choice = {
  id: string;
  text: string;
};

export type McQuestion = {
  id: string;
  type: "mc";
  prompt: string;
  choices: Choice[];
  correctChoiceId: string;
  source: string;
  sourceSectionTitle?: string;
};

export type TfQuestion = {
  id: string;
  type: "tf";
  prompt: string;
  statement: string;
  correct: boolean;
  source: string;
  sourceSectionTitle?: string;
};

export type Question = McQuestion | TfQuestion;

export type StudySection = {
  id: string;
  title: string;
  questions: Question[];
};
