#!/usr/bin/env bun
/**
 * AgentFactory.ts - Dynamic Agent Composition Engine
 *
 * Creates specialized agents by combining traits from Data/Traits.yaml.
 * Outputs full agent prompts with voice IDs for TTS integration.
 *
 * Usage:
 *   bun run AgentFactory.ts --traits "security,skeptical,thorough" --task "Review this code"
 *   bun run AgentFactory.ts --list
 *   bun run AgentFactory.ts --traits "research,enthusiastic" --output json
 */

import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { homedir } from 'os';
import { parse as parseYaml } from 'yaml';
import Handlebars from 'handlebars';

// ============================================================================
// Configuration
// ============================================================================

const PAI_DIR = process.env.PAI_DIR || join(homedir(), '.config', 'pai');
const TRAITS_FILE = join(PAI_DIR, 'skills', 'Agents', 'Data', 'Traits.yaml');
const TEMPLATE_FILE = join(PAI_DIR, 'skills', 'Agents', 'Templates', 'DynamicAgent.hbs');

// ============================================================================
// Types
// ============================================================================

interface Trait {
  name: string;
  prompt_fragment: string;
  voice_id: string;
  description: string;
  keywords?: string[];
}

interface TraitsConfig {
  version: string;
  expertise: Record<string, Trait>;
  personality: Record<string, Trait>;
  approach: Record<string, Trait>;
}

interface ComposedAgent {
  name: string;
  expertise: Trait[];
  personality: Trait[];
  approach: Trait[];
  voiceId: string;
  voice: string;
  task?: string;
  prompt: string;
}

// ============================================================================
// Trait Loading
// ============================================================================

function loadTraits(): TraitsConfig {
  if (!existsSync(TRAITS_FILE)) {
    console.error(`Traits file not found: ${TRAITS_FILE}`);
    process.exit(1);
  }

  const content = readFileSync(TRAITS_FILE, 'utf-8');
  return parseYaml(content) as TraitsConfig;
}

function loadTemplate(): HandlebarsTemplateDelegate {
  if (!existsSync(TEMPLATE_FILE)) {
    console.error(`Template file not found: ${TEMPLATE_FILE}`);
    process.exit(1);
  }

  const content = readFileSync(TEMPLATE_FILE, 'utf-8');
  return Handlebars.compile(content);
}

// ============================================================================
// Trait Inference
// ============================================================================

function inferTraitsFromTask(task: string, traits: TraitsConfig): string[] {
  const inferred: string[] = [];
  const taskLower = task.toLowerCase();

  // Check expertise keywords
  for (const [key, def] of Object.entries(traits.expertise)) {
    if (def.keywords?.some((kw) => taskLower.includes(kw.toLowerCase()))) {
      inferred.push(key);
    }
  }

  // Check personality keywords
  for (const [key, def] of Object.entries(traits.personality)) {
    if (def.keywords?.some((kw) => taskLower.includes(kw.toLowerCase()))) {
      inferred.push(key);
    }
  }

  // Check approach keywords
  for (const [key, def] of Object.entries(traits.approach)) {
    if (def.keywords?.some((kw) => taskLower.includes(kw.toLowerCase()))) {
      inferred.push(key);
    }
  }

  // Apply smart defaults if no traits found
  const hasExpertise = inferred.some((t) => traits.expertise[t]);
  const hasPersonality = inferred.some((t) => traits.personality[t]);
  const hasApproach = inferred.some((t) => traits.approach[t]);

  if (!hasPersonality) inferred.push("analytical");
  if (!hasApproach) inferred.push("thorough");
  if (!hasExpertise) inferred.push("research");

  return [...new Set(inferred)];
}

// ============================================================================
// Trait Resolution
// ============================================================================

function resolveTrait(traits: TraitsConfig, traitId: string): { category: string; trait: Trait } | null {
  const categories = ['expertise', 'personality', 'approach'] as const;

  for (const category of categories) {
    const categoryTraits = traits[category];
    if (categoryTraits[traitId]) {
      return { category, trait: categoryTraits[traitId] };
    }
  }

  return null;
}

function selectVoice(expertise: Trait[], personality: Trait[], approach: Trait[]): { voiceId: string; voice: string } {
  // Priority: personality > approach > expertise
  // This reflects that "how you communicate" is more about personality than knowledge

  if (personality.length > 0 && personality[0].voice_id) {
    return { voiceId: personality[0].voice_id, voice: personality[0].name };
  }

  if (approach.length > 0 && approach[0].voice_id) {
    return { voiceId: approach[0].voice_id, voice: approach[0].name };
  }

  if (expertise.length > 0 && expertise[0].voice_id) {
    return { voiceId: expertise[0].voice_id, voice: expertise[0].name };
  }

  return { voiceId: 'default_voice', voice: 'Default' };
}

// ============================================================================
// Agent Composition
// ============================================================================

function composeAgent(traitIds: string[], task?: string): ComposedAgent {
  const traits = loadTraits();
  const template = loadTemplate();

  const expertise: Trait[] = [];
  const personality: Trait[] = [];
  const approach: Trait[] = [];

  // Resolve each trait
  for (const traitId of traitIds) {
    const resolved = resolveTrait(traits, traitId.trim().toLowerCase());
    if (!resolved) {
      console.warn(`Unknown trait: ${traitId}`);
      continue;
    }

    switch (resolved.category) {
      case 'expertise':
        expertise.push(resolved.trait);
        break;
      case 'personality':
        personality.push(resolved.trait);
        break;
      case 'approach':
        approach.push(resolved.trait);
        break;
    }
  }

  // Generate agent name from traits
  const nameParts = [
    ...expertise.map(t => t.name.split(' ')[0]),
    ...personality.map(t => t.name),
    ...approach.map(t => t.name),
  ].slice(0, 3);

  const name = nameParts.length > 0 ? nameParts.join(' ') : 'General Agent';

  // Select voice based on traits
  const { voiceId, voice } = selectVoice(expertise, personality, approach);

  // Render prompt
  const promptData = {
    name,
    expertise,
    personality,
    approach,
    voiceId,
    voice,
    task,
  };

  const prompt = template(promptData);

  return {
    name,
    expertise,
    personality,
    approach,
    voiceId,
    voice,
    task,
    prompt,
  };
}

// ============================================================================
// List Traits
// ============================================================================

function listTraits(): void {
  const traits = loadTraits();

  console.log('\nAVAILABLE TRAITS\n');

  console.log('EXPERTISE (domain knowledge):');
  for (const [id, trait] of Object.entries(traits.expertise)) {
    console.log(`  ${id.padEnd(15)} - ${trait.name}`);
  }

  console.log('\nPERSONALITY (behavior style):');
  for (const [id, trait] of Object.entries(traits.personality)) {
    console.log(`  ${id.padEnd(15)} - ${trait.name}`);
  }

  console.log('\nAPPROACH (work style):');
  for (const [id, trait] of Object.entries(traits.approach)) {
    console.log(`  ${id.padEnd(15)} - ${trait.name}`);
  }

  const totalCombinations =
    Object.keys(traits.expertise).length *
    Object.keys(traits.personality).length *
    Object.keys(traits.approach).length;

  console.log(`\nTotal possible combinations: ${totalCombinations}`);
}

// ============================================================================
// CLI
// ============================================================================

function parseArgs(): { traits?: string; task?: string; output?: string; list?: boolean; help?: boolean } {
  const args = process.argv.slice(2);
  const result: Record<string, string | boolean> = {};

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === '--help' || arg === '-h') {
      result.help = true;
    } else if (arg === '--list' || arg === '-l') {
      result.list = true;
    } else if (arg === '--traits' || arg === '-t') {
      result.traits = args[++i];
    } else if (arg === '--task') {
      result.task = args[++i];
    } else if (arg === '--output' || arg === '-o') {
      result.output = args[++i];
    }
  }

  return result;
}

function showHelp(): void {
  console.log(`
AgentFactory - Dynamic Agent Composition Engine

Usage:
  bun run AgentFactory.ts --task <description> [--output <format>]
  bun run AgentFactory.ts --traits <trait1,trait2,...> [--task <description>] [--output <format>]
  bun run AgentFactory.ts --list

Options:
  -t, --task <desc>       Task description (traits will be inferred from keywords)
  -r, --traits <traits>   Comma-separated list of traits (optional if --task provided)
  -o, --output <format>   Output format: text (default), json, prompt, yaml, summary
  -l, --list              List all available traits
  -h, --help              Show this help

Examples:
  bun run AgentFactory.ts --task "Review this security architecture"
  bun run AgentFactory.ts --traits "security,skeptical,thorough" --task "Review this code"
  bun run AgentFactory.ts --traits "research,enthusiastic" --output json
  bun run AgentFactory.ts --list
`);
}

function main(): void {
  const args = parseArgs();

  if (args.help) {
    showHelp();
    return;
  }

  if (args.list) {
    listTraits();
    return;
  }

  const traits = loadTraits();
  let traitIds: string[] = [];

  // Get explicit traits if provided
  if (args.traits) {
    traitIds = args.traits.split(',').map(t => t.trim().toLowerCase());
  }

  // Infer traits from task if provided
  if (args.task) {
    const inferred = inferTraitsFromTask(args.task, traits);
    traitIds = [...new Set([...traitIds, ...inferred])];
  }

  if (traitIds.length === 0) {
    console.error('Error: Provide --task or --traits. Use --help for usage.');
    process.exit(1);
  }

  const agent = composeAgent(traitIds, args.task);

  switch (args.output) {
    case 'json':
      console.log(JSON.stringify({
        name: agent.name,
        voice_id: agent.voiceId,
        voice: agent.voice,
        expertise: agent.expertise.map(t => t.name),
        personality: agent.personality.map(t => t.name),
        approach: agent.approach.map(t => t.name),
        task: agent.task,
        prompt: agent.prompt,
      }, null, 2));
      break;

    case 'prompt':
      console.log(agent.prompt);
      break;

    default:
      console.log('\n=== COMPOSED AGENT ===\n');
      console.log(`Name: ${agent.name}`);
      console.log(`Voice: ${agent.voice} (${agent.voiceId})`);
      console.log(`\nExpertise: ${agent.expertise.map(t => t.name).join(', ') || 'None'}`);
      console.log(`Personality: ${agent.personality.map(t => t.name).join(', ') || 'None'}`);
      console.log(`Approach: ${agent.approach.map(t => t.name).join(', ') || 'None'}`);
      if (agent.task) {
        console.log(`\nTask: ${agent.task}`);
      }
      console.log('\n=== FULL PROMPT ===\n');
      console.log(agent.prompt);
      break;
  }
}

if (import.meta.main) {
  main();
}

export { composeAgent, loadTraits, listTraits };
