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
	import ConfettiEffect from '$lib/components/gamification/ConfettiEffect.svelte';
	import { showPointsToast, showAchievementToast, showToast } from '$lib/stores/toast';
	import AnimatedCounter from '$lib/components/gamification/AnimatedCounter.svelte';
	import { mdiCalendarToday, mdiAlertCircle, mdiStar, mdiPartyPopper } from '@mdi/js';

	let rooms = $state<Room[]>([]);
	let instances = $state<TaskInstanceWithDetails[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let tasksToday = $state(0);
	let tasksOverdue = $state(0);

	// Complete-Modal
	let completeModalOpen = $state(false);
	let selectedInstance = $state<TaskInstanceWithDetails | null>(null);

	// Punkte-Animation + Confetti
	let pointsAnim = $state<{ points: number; bonus: number } | null>(null);
	let showConfetti = $state(false);

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
			const [dashboard, todayInstances, roomList] = await Promise.all([
				client.dashboard.get(),
				client.instances.today(),
				client.rooms.list()
			]);

			rooms = roomList;
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

			// Punkte-Animation + Confetti
			pointsAnim = { points: result.bonus_breakdown.total_points, bonus: result.bonus_breakdown.bonus_points };
			showConfetti = true;
			setTimeout(() => { pointsAnim = null; }, 1500);
			setTimeout(() => { showConfetti = false; }, 2000);

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
		<Card class="gradient-card-blue border-0">
			<div class="flex flex-col items-center text-center">
				<Icon path={mdiCalendarToday} size={24} class="text-primary-600 dark:text-primary-300 mb-1" />
				<span class="text-2xl font-bold"><AnimatedCounter value={tasksToday} /></span>
				<span class="text-xs text-primary-700/70 dark:text-primary-300/70">Heute</span>
			</div>
		</Card>
		<Card class="{tasksOverdue > 0 ? 'border-danger-500 animate-pulse-glow-red' : ''}">
			<div class="flex flex-col items-center text-center">
				<Icon path={mdiAlertCircle} size={24} class={tasksOverdue > 0 ? 'text-danger-500' : 'text-gray-400'} />
				<span class="text-2xl font-bold" class:text-danger-500={tasksOverdue > 0}><AnimatedCounter value={tasksOverdue} /></span>
				<span class="text-xs text-gray-500 dark:text-gray-400">Überfällig</span>
			</div>
		</Card>
		<Card class="gradient-card-gold border-0 relative overflow-hidden">
			<div class="absolute inset-0 animate-shimmer pointer-events-none"></div>
			<div class="flex flex-col items-center text-center relative">
				<Icon path={mdiStar} size={24} class="text-yellow-600 dark:text-yellow-300 mb-1" />
				<span class="text-2xl font-bold"><AnimatedCounter value={currentUser?.weekly_points ?? 0} /></span>
				<span class="text-xs text-yellow-700/70 dark:text-yellow-300/70">Woche</span>
			</div>
		</Card>
	</div>

	<!-- Aufgaben nach Raum -->
	{#if instances.length === 0}
		<Card class="text-center py-8">
			<Icon path={mdiPartyPopper} size={48} class="text-accent-500 mx-auto mb-3" />
			<p class="text-lg font-semibold mb-1">Alles erledigt!</p>
			<p class="text-gray-500 dark:text-gray-400">Keine Aufgaben mehr für heute. Genieße den Rest des Tages!</p>
		</Card>
	{:else}
		{#each rooms.toSorted((a, b) => a.sort_order - b.sort_order) as room (room.id)}
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
		<PointsAnimation points={pointsAnim.points} bonus={pointsAnim.bonus} />
	{/if}

	{#if showConfetti}
		<ConfettiEffect />
	{/if}
{/if}
