import { parse, format } from "./codec";

export const read = (text: string) => parse(text);
