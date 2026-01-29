<script lang="ts">
	import { onMount } from 'svelte';
	import { createApiClient, ApiError } from '$lib/api/client';
	import { apiBaseUrl, apiKey } from '$lib/stores/config';
	import { selectedUser, selectedUserId } from '$lib/stores/user';
	import type { Room, TaskInstanceWithDetails, ExtendedCompletionResponse } from '$lib/api/types';
	import Card from '$lib/components/ui/Card.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Icon from '$lib/components/ui/Icon.svelte';
	import Loading from '$lib/components/shared/Loading.svelte';
	import ErrorMessage from '$lib/components/shared/ErrorMessage.svelte';
	import RoomSection from '$lib/components/dashboard/RoomSection.svelte';
	import QuickCompleteModal from '$lib/components/dashboard/QuickCompleteModal.svelte';
	import PointsAnimation from '$lib/components/gamification/PointsAnimation.svelte';
	import { showPointsToast, showAchievementToast, showToast } from '$lib/stores/toast';
	import { mdiCalendarToday, mdiAlertCircle, mdiStar } from '@mdi/js';

	let rooms = $state<Room[]>([]);
	let instances = $state<TaskInstanceWithDetails[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let tasksToday = $state(0);
	let tasksOverdue = $state(0);

	// Complete-Modal
	let completeModalOpen = $state(false);
	let selectedInstance = $state<TaskInstanceWithDetails | null>(null);

	// Punkte-Animation
	let pointsAnim = $state<{ points: number; x: number; y: number } | null>(null);

	async function loadData() {
		if (!$apiKey) {
			error = 'Bitte konfiguriere die API-Verbindung in den Einstellungen.';
			loading = false;
			return;
		}

		loading = true;
		error = null;

		try {
			const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
			const [dashboard, todayInstances] = await Promise.all([
				client.dashboard.get(),
				client.instances.today()
			]);

			rooms = dashboard.rooms;
			instances = todayInstances;
			tasksToday = dashboard.tasks_today;
			tasksOverdue = dashboard.tasks_overdue;
		} catch (e) {
			error = e instanceof ApiError ? e.detail : 'Verbindung fehlgeschlagen';
		} finally {
			loading = false;
		}
	}

	function openComplete(instance: TaskInstanceWithDetails) {
		selectedInstance = instance;
		completeModalOpen = true;
	}

	async function handleComplete(instanceId: number, userId: number, notes: string) {
		const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
		try {
			const result: ExtendedCompletionResponse = await client.instances.complete(instanceId, {
				user_id: userId,
				notes: notes || undefined
			});

			completeModalOpen = false;
			showPointsToast(result.bonus_breakdown.total_points, result.bonus_breakdown.bonus_points);

			for (const ach of result.unlocked_achievements) {
				showAchievementToast(ach.name);
			}

			// Punkte-Animation
			pointsAnim = { points: result.bonus_breakdown.total_points, x: 0, y: 0 };
			setTimeout(() => { pointsAnim = null; }, 1500);

			await loadData();
		} catch (e) {
			showToast(e instanceof ApiError ? e.detail : 'Fehler beim Erledigen', 'error');
		}
	}

	onMount(loadData);

	// Gruppiere Instanzen nach Raum
	let instancesByRoom = $derived.by(() => {
		const map = new Map<number, TaskInstanceWithDetails[]>();
		for (const inst of instances) {
			const roomId = inst.task.room_id;
			if (!map.has(roomId)) map.set(roomId, []);
			map.get(roomId)!.push(inst);
		}
		return map;
	});

	let currentUser = $derived($selectedUser);
</script>

<svelte:head>
	<title>ChoreQuest - Übersicht</title>
</svelte:head>

{#if loading}
	<Loading />
{:else if error}
	<ErrorMessage message={error} onretry={loadData} />
{:else}
	<!-- Stat-Cards -->
	<div class="grid grid-cols-3 gap-3 mb-6">
		<Card>
			<div class="flex flex-col items-center text-center">
				<Icon path={mdiCalendarToday} size={24} class="text-primary-500 mb-1" />
				<span class="text-2xl font-bold">{tasksToday}</span>
				<span class="text-xs text-gray-500 dark:text-gray-400">Heute</span>
			</div>
		</Card>
		<Card class={tasksOverdue > 0 ? 'border-danger-500/50' : ''}>
			<div class="flex flex-col items-center text-center">
				<Icon path={mdiAlertCircle} size={24} class={tasksOverdue > 0 ? 'text-danger-500' : 'text-gray-400'} />
				<span class="text-2xl font-bold" class:text-danger-500={tasksOverdue > 0}>{tasksOverdue}</span>
				<span class="text-xs text-gray-500 dark:text-gray-400">Überfällig</span>
			</div>
		</Card>
		<Card>
			<div class="flex flex-col items-center text-center">
				<Icon path={mdiStar} size={24} class="text-accent-500 mb-1" />
				<span class="text-2xl font-bold">{currentUser?.weekly_points ?? 0}</span>
				<span class="text-xs text-gray-500 dark:text-gray-400">Woche</span>
			</div>
		</Card>
	</div>

	<!-- Aufgaben nach Raum -->
	{#if instances.length === 0}
		<Card class="text-center py-8">
			<p class="text-gray-500 dark:text-gray-400">Keine Aufgaben für heute.</p>
		</Card>
	{:else}
		{#each rooms.sort((a, b) => a.sort_order - b.sort_order) as room (room.id)}
			{@const roomInstances = instancesByRoom.get(room.id) ?? []}
			{#if roomInstances.length > 0}
				<RoomSection {room} instances={roomInstances} oncomplete={openComplete} />
			{/if}
		{/each}
	{/if}

	<QuickCompleteModal
		open={completeModalOpen}
		instance={selectedInstance}
		onclose={() => { completeModalOpen = false; }}
		oncomplete={handleComplete}
	/>

	{#if pointsAnim}
		<PointsAnimation points={pointsAnim.points} />
	{/if}
{/if}
