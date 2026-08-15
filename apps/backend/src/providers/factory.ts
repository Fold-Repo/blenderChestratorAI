import { OpenAIResponsesProvider } from './openaiResponsesProvider.js';
import { RuleBasedSceneProvider } from './ruleBasedSceneProvider.js';
import type { AIProvider } from './types.js';

export const createSceneProvider = (): AIProvider => {
  const apiKey = process.env.OPENAI_API_KEY;
  if (apiKey)
    return new OpenAIResponsesProvider({
      apiKey,
      model: process.env.OPENAI_MODEL,
    });
  return new RuleBasedSceneProvider();
};
