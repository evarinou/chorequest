import type {
	User, UserCreate, UserUpdate, UserStats,
	Room, RoomCreate, RoomUpdate,
	Task, TaskCreate, TaskUpdate,
	TaskInstanceWithDetails,
	CompleteRequest, ExtendedCompletionResponse,
	Achievement, UserAchievement, AchievementProgress,
	DashboardResponse, HealthResponse, TaskInstance,
	WeeklySummary, GenerateSummaryResponse
} from './types';

type Fetch = typeof fetch;

class ApiError extends Error {
	constructor(public status: number, public detail: string) {
		super(detail);
		this.name = 'ApiError';
	}
}

export { ApiError };

export function createApiClient(fetchFn: Fetch, baseUrl: string, apiKey: string) {
	async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
		const res = await fetchFn(`${baseUrl}${path}`, {
			method,
			headers: {
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${apiKey}`
			},
			body: body ? JSON.stringify(body) : undefined
		});

		if (!res.ok) {
			let detail = `HTTP ${res.status}`;
			try {
				const err = await res.json();
				detail = err.detail || detail;
			} catch { /* ignore */ }
			throw new ApiError(res.status, detail);
		}

		if (res.status === 204) return undefined as T;
		return res.json();
	}

	return {
		health: {
			check: () => request<HealthResponse>('GET', '/api/health')
		},

		dashboard: {
			get: () => request<DashboardResponse>('GET', '/api/dashboard')
		},

		users: {
			list: () => request<User[]>('GET', '/api/users'),
			get: (id: number) => request<User>('GET', `/api/users/${id}`),
			create: (data: UserCreate) => request<User>('POST', '/api/users', data),
			update: (id: number, data: UserUpdate) => request<User>('PATCH', `/api/users/${id}`, data),
			stats: (id: number) => request<UserStats>('GET', `/api/users/${id}/stats`)
		},

		rooms: {
			list: () => request<Room[]>('GET', '/api/rooms'),
			create: (data: RoomCreate) => request<Room>('POST', '/api/rooms', data),
			update: (id: number, data: RoomUpdate) => request<Room>('PATCH', `/api/rooms/${id}`, data),
			delete: (id: number) => request<void>('DELETE', `/api/rooms/${id}`)
		},

		tasks: {
			list: (params?: { room_id?: number; is_active?: boolean }) => {
				const qs = new URLSearchParams();
				if (params?.room_id != null) qs.set('room_id', String(params.room_id));
				if (params?.is_active != null) qs.set('is_active', String(params.is_active));
				const q = qs.toString();
				return request<Task[]>('GET', `/api/tasks${q ? '?' + q : ''}`);
			},
			create: (data: TaskCreate) => request<Task>('POST', '/api/tasks', data),
			get: (id: number) => request<Task>('GET', `/api/tasks/${id}`),
			update: (id: number, data: TaskUpdate) => request<Task>('PATCH', `/api/tasks/${id}`, data),
			delete: (id: number) => request<void>('DELETE', `/api/tasks/${id}`)
		},

		instances: {
			list: (params?: { room_id?: number; user_id?: number; status?: string; due_date?: string }) => {
				const qs = new URLSearchParams();
				if (params?.room_id != null) qs.set('room_id', String(params.room_id));
				if (params?.user_id != null) qs.set('user_id', String(params.user_id));
				if (params?.status) qs.set('status', params.status);
				if (params?.due_date) qs.set('due_date', params.due_date);
				const q = qs.toString();
				return request<TaskInstanceWithDetails[]>('GET', `/api/instances${q ? '?' + q : ''}`);
			},
			today: () => request<TaskInstanceWithDetails[]>('GET', '/api/instances/today'),
			complete: (id: number, data: CompleteRequest) =>
				request<ExtendedCompletionResponse>('POST', `/api/instances/${id}/complete`, data),
			skip: (id: number) => request<TaskInstance>('POST', `/api/instances/${id}/skip`),
			assign: (id: number, userId: number) =>
				request<TaskInstance>('POST', `/api/instances/${id}/assign`, { user_id: userId })
		},

		summaries: {
			list: (limit?: number) => {
				const qs = limit ? `?limit=${limit}` : '';
				return request<WeeklySummary[]>('GET', `/api/summaries${qs}`);
			},
			latest: () => request<WeeklySummary>('GET', '/api/summaries/latest'),
			generate: (weekStart?: string) =>
				request<GenerateSummaryResponse>('POST', '/api/summaries/generate',
					weekStart ? { week_start: weekStart } : undefined
				)
		},

		gamification: {
			leaderboard: () => request<User[]>('GET', '/api/leaderboard'),
			leaderboardWeekly: () => request<User[]>('GET', '/api/leaderboard/weekly'),
			achievements: () => request<Achievement[]>('GET', '/api/achievements'),
			userAchievements: (userId: number) =>
				request<UserAchievement[]>('GET', `/api/achievements/${userId}`),
			userProgress: (userId: number) =>
				request<AchievementProgress[]>('GET', `/api/achievements/${userId}/progress`)
		}
	};
}

export type ApiClient = ReturnType<typeof createApiClient>;
