/**
 * Shared types and utilities for cat-now-me monorepo
 * Used by both web (Next.js) and api (FastAPI via Python bindings)
 */

// ============================================
// Base Types
// ============================================

export interface BaseEntity {
  id: string;
  createdAt: string;
  updatedAt: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
  meta?: Record<string, unknown>;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

// ============================================
// User & Auth Types
// ============================================

export interface User extends BaseEntity {
  email: string;
  name: string;
  avatar?: string;
  role: UserRole;
  preferences: UserPreferences;
}

export type UserRole = 'admin' | 'client' | 'viewer';

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  notifications: NotificationSettings;
  language: string;
}

export interface NotificationSettings {
  email: boolean;
  push: boolean;
  inApp: boolean;
}

// ============================================
// Project Types (for client websites)
// ============================================

export interface Project extends BaseEntity {
  name: string;
  slug: string;
  description: string;
  status: ProjectStatus;
  clientId: string;
  techStack: string[];
  repositoryUrl?: string;
  deployedUrl?: string;
  previewUrl?: string;
  startDate: string;
  deadline?: string;
  tags: string[];
}

export type ProjectStatus = 
  | 'discovery' 
  | 'design' 
  | 'development' 
  | 'review' 
  | 'deployed' 
  | 'maintenance' 
  | 'archived';

export interface ProjectMilestone extends BaseEntity {
  projectId: string;
  title: string;
  description: string;
  dueDate: string;
  status: MilestoneStatus;
  assigneeId?: string;
}

export type MilestoneStatus = 'pending' | 'in_progress' | 'completed' | 'blocked';

// ============================================
// AI Agent Types
// ============================================

export interface AgentConfig {
  id: string;
  name: string;
  description: string;
  model: string; // Ollama model name
  systemPrompt: string;
  tools: AgentTool[];
  temperature: number;
  maxTokens: number;
}

export interface AgentTool {
  name: string;
  description: string;
  schema: Record<string, unknown>; // JSON Schema
}

export interface AgentRun extends BaseEntity {
  agentId: string;
  input: Record<string, unknown>;
  output?: Record<string, unknown>;
  status: AgentRunStatus;
  steps: AgentStep[];
  error?: string;
  startedAt: string;
  completedAt?: string;
  tokensUsed?: number;
}

export type AgentRunStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface AgentStep {
  id: string;
  type: 'llm' | 'tool' | 'condition' | 'human';
  input: Record<string, unknown>;
  output?: Record<string, unknown>;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startedAt: string;
  completedAt?: string;
}

// ============================================
// Automation / n8n Types
// ============================================

export interface Workflow extends BaseEntity {
  name: string;
  description: string;
  n8nId?: string; // n8n workflow ID
  status: WorkflowStatus;
  triggers: WorkflowTrigger[];
  webhookUrl?: string;
}

export type WorkflowStatus = 'draft' | 'active' | 'paused' | 'archived';

export interface WorkflowTrigger {
  type: 'webhook' | 'schedule' | 'manual' | 'event';
  config: Record<string, unknown>;
}

export interface WorkflowExecution extends BaseEntity {
  workflowId: string;
  status: ExecutionStatus;
  input: Record<string, unknown>;
  output?: Record<string, unknown>;
  error?: string;
  startedAt: string;
  completedAt?: string;
  durationMs?: number;
}

export type ExecutionStatus = 'running' | 'success' | 'failed' | 'cancelled';

// ============================================
// Content / CMS Types
// ============================================

export interface ContentBlock extends BaseEntity {
  projectId: string;
  type: ContentBlockType;
  title: string;
  content: Record<string, unknown>;
  order: number;
  isPublished: boolean;
  seo?: SeoData;
}

export type ContentBlockType = 
  | 'hero' 
  | 'about' 
  | 'services' 
  | 'testimonials' 
  | 'gallery' 
  | 'contact' 
  | 'blog' 
  | 'faq' 
  | 'cta' 
  | 'custom';

export interface SeoData {
  title: string;
  description: string;
  keywords: string[];
  ogImage?: string;
  canonicalUrl?: string;
  noIndex: boolean;
  noFollow: boolean;
}

// ============================================
// Utility Functions
// ============================================

export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
}

export function slugify(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

export function formatDate(date: Date | string, options?: Intl.DateTimeFormatOptions): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...options,
  });
}

export function classNames(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ');
}

export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function retry<T>(
  fn: () => Promise<T>,
  retries: number = 3,
  delayMs: number = 1000
): Promise<T> {
  return fn().catch(err => {
    if (retries <= 0) throw err;
    return sleep(delayMs).then(() => retry(fn, retries - 1, delayMs * 2));
  });
}