<script lang="ts">
	import { onMount } from 'svelte';
	import { createApiClient, ApiError } from '$lib/api/client';
	import { apiBaseUrl, apiKey } from '$lib/stores/config';
	import { selectedUser, selectedUserId } from '$lib/stores/user';
	import type { Room, TaskInstanceWithDetails, ExtendedCompletionResponse } from '$lib/api/types';
	import Card from '$lib/components/ui/Card.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Loading from '$lib/components/shared/Loading.svelte';
	import ErrorMessage from '$lib/components/shared/ErrorMessage.svelte';
	import RoomSection from '$lib/components/dashboard/RoomSection.svelte';
	import QuickCompleteModal from '$lib/components/dashboard/QuickCompleteModal.svelte';
	import PointsAnimation from '$lib/components/gamification/PointsAnimation.svelte';
	import ConfettiEffect from '$lib/components/gamification/ConfettiEffect.svelte';
	import LevelUpOverlay from '$lib/components/gamification/LevelUpOverlay.svelte';
	import { showPointsToast, showAchievementToast, showToast } from '$lib/stores/toast';
	import AnimatedCounter from '$lib/components/gamification/AnimatedCounter.svelte';
	import { getLevelInfo } from '$lib/utils/level';

	let rooms = $state<Room[]>([]);
	let instances = $state<TaskInstanceWithDetails[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let tasksToday = $state(0);
	let tasksOverdue = $state(0);

	let completeModalOpen = $state(false);
	let selectedInstance = $state<TaskInstanceWithDetails | null>(null);

	let pointsAnim = $state<{ points: number; bonus: number } | null>(null);
	let showConfetti = $state(false);
	let levelUpData = $state<{ oldLevel: ReturnType<typeof getLevelInfo>; newLevel: ReturnType<typeof getLevelInfo> } | null>(null);

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
		const currentUser = $selectedUser;
		const oldLevelInfo = currentUser ? getLevelInfo(currentUser.total_points) : null;

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

			pointsAnim = { points: result.bonus_breakdown.total_points, bonus: result.bonus_breakdown.bonus_points };
			showConfetti = true;
			setTimeout(() => { pointsAnim = null; }, 1500);
			setTimeout(() => { showConfetti = false; }, 2500);

			await loadData();

			// Check level up
			if (oldLevelInfo && currentUser) {
				const newUser = $selectedUser;
				if (newUser) {
					const newLevelInfo = getLevelInfo(newUser.total_points);
					if (newLevelInfo.level > oldLevelInfo.level) {
						levelUpData = { oldLevel: oldLevelInfo, newLevel: newLevelInfo };
						setTimeout(() => { levelUpData = null; }, 3000);
					}
				}
			}
		} catch (e) {
			showToast(e instanceof ApiError ? e.detail : 'Fehler beim Erledigen', 'error');
		}
	}

	onMount(loadData);

	let today = $derived(new Date().toLocaleDateString('sv-SE'));

	let allPending = $derived(instances.filter((i) => i.status === 'pending'));

	let sortedInstances = $derived.by(() => {
		const statusOrder = (i: TaskInstanceWithDetails) => {
			if (i.status === 'pending' && i.due_date && i.due_date < today) return 0; // überfällig pending
			if (i.status === 'pending') return 1; // heute pending
			if (i.status === 'completed') return 2;
			return 3; // skipped
		};
		return [...instances].sort((a, b) => statusOrder(a) - statusOrder(b) || a.id - b.id);
	});

	let instancesByRoom = $derived.by(() => {
		const map = new Map<number, TaskInstanceWithDetails[]>();
		for (const inst of sortedInstances) {
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
	<div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
		<Card>
			<div class="flex flex-col items-center text-center">
				<span class="text-[8px] text-nes-blue dark:text-crt-green mb-1" style="font-family: 'Press Start 2P', monospace;">TAGES-QUESTS</span>
				<span class="text-3xl font-bold text-nes-blue dark:text-crt-green"><AnimatedCounter value={tasksToday} /></span>
			</div>
		</Card>
		<Card class="{tasksOverdue > 0 ? 'border-nes-red!' : ''}">
			<div class="flex flex-col items-center text-center">
				<span class="text-[8px] mb-1 {tasksOverdue > 0 ? 'text-nes-red animate-pixel-blink' : 'text-parchment-400 dark:text-crt-green/60'}" style="font-family: 'Press Start 2P', monospace;">
					{tasksOverdue > 0 ? 'VERPASST!' : 'VERPASST'}
				</span>
				<span class="text-3xl font-bold" class:text-nes-red={tasksOverdue > 0}><AnimatedCounter value={tasksOverdue} /></span>
			</div>
		</Card>
		<Card class="pixel-border-gold">
			<div class="flex flex-col items-center text-center">
				<span class="text-[8px] text-nes-gold mb-1" style="font-family: 'Press Start 2P', monospace;">WOCHEN-XP</span>
				<span class="text-3xl font-bold text-nes-gold"><AnimatedCounter value={currentUser?.weekly_points ?? 0} /></span>
			</div>
		</Card>
	</div>

	<!-- Aufgaben nach Raum -->
	{#if allPending.length === 0}
		<Card class="text-center py-8">
			<div class="text-4xl mb-3">🎉</div>
			<p class="text-[10px] mb-2" style="font-family: 'Press Start 2P', monospace;">ALLES ERLEDIGT!</p>
			<p class="text-parchment-400 dark:text-crt-green/60">Keine Quests mehr für heute.</p>
		</Card>
	{/if}

	{#each rooms.toSorted((a, b) => a.sort_order - b.sort_order) as room (room.id)}
		{@const roomInstances = instancesByRoom.get(room.id) ?? []}
		{#if roomInstances.length > 0}
			<RoomSection {room} instances={roomInstances} oncomplete={openComplete} />
		{/if}
	{/each}

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

	{#if levelUpData}
		<LevelUpOverlay oldLevel={levelUpData.oldLevel} newLevel={levelUpData.newLevel} />
	{/if}
{/if}
