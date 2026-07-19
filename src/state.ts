import type { Env, UserState } from "./types";

const MAX_HISTORY = 20;

function key(userId: number): string {
  return `user:${userId}`;
}

export async function getUserState(env: Env, userId: number): Promise<UserState> {
  const raw = await env.BOT_KV.get(key(userId));
  if (!raw) return { favorites: [], history: [] };
  try {
    return JSON.parse(raw) as UserState;
  } catch {
    return { favorites: [], history: [] };
  }
}

export async function saveUserState(env: Env, userId: number, state: UserState): Promise<void> {
  await env.BOT_KV.put(key(userId), JSON.stringify(state));
}

export async function addFavorite(env: Env, userId: number, commandId: string): Promise<UserState> {
  const state = await getUserState(env, userId);
  if (!state.favorites.includes(commandId)) {
    state.favorites.unshift(commandId);
  }
  await saveUserState(env, userId, state);
  return state;
}

export async function removeFavorite(env: Env, userId: number, commandId: string): Promise<UserState> {
  const state = await getUserState(env, userId);
  state.favorites = state.favorites.filter((id) => id !== commandId);
  await saveUserState(env, userId, state);
  return state;
}

export async function pushHistory(env: Env, userId: number, commandId: string): Promise<void> {
  const state = await getUserState(env, userId);
  state.history = [commandId, ...state.history.filter((id) => id !== commandId)].slice(0, MAX_HISTORY);
  await saveUserState(env, userId, state);
}
