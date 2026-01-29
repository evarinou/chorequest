<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { createApiClient, ApiError } from '$lib/api/client';
	import { apiBaseUrl, apiKey } from '$lib/stores/config';
	import { showToast } from '$lib/stores/toast';
	import type { Task, Room, TaskUpdate } from '$lib/api/types';
	import TaskForm from '$lib/components/tasks/TaskForm.svelte';
	import Loading from '$lib/components/shared/Loading.svelte';
	import ErrorMessage from '$lib/components/shared/ErrorMessage.svelte';

	let { data } = $props();

	let task = $state<Task | null>(null);
	let rooms = $state<Room[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let submitting = $state(false);

	async function loadData() {
		loading = true;
		error = null;
		try {
			const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
			const [t, r] = await Promise.all([
				client.tasks.get(data.taskId),
				client.rooms.list()
			]);
			task = t;
			rooms = r;
		} catch (e) {
			error = e instanceof ApiError ? e.detail : 'Fehler beim Laden';
		} finally {
			loading = false;
		}
	}

	async function handleSubmit(updates: TaskUpdate) {
		submitting = true;
		try {
			const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
			await client.tasks.update(data.taskId, updates as TaskUpdate);
			showToast('Aufgabe aktualisiert', 'success');
			goto('/aufgaben');
		} catch (e) {
			showToast(e instanceof ApiError ? e.detail : 'Fehler beim Speichern', 'error');
		} finally {
			submitting = false;
		}
	}

	onMount(loadData);
</script>

<svelte:head>
	<title>Aufgabe bearbeiten - ChoreQuest</title>
</svelte:head>

<h1 class="text-2xl font-bold mb-6">Aufgabe bearbeiten</h1>

{#if loading}
	<Loading />
{:else if error}
	<ErrorMessage message={error} onretry={loadData} />
{:else if task}
	<TaskForm
		{rooms}
		initial={{
			title: task.title,
			description: task.description,
			room_id: task.room_id,
			base_points: task.base_points,
			estimated_minutes: task.estimated_minutes,
			recurrence: task.recurrence,
			recurrence_day: task.recurrence_day,
			is_active: task.is_active
		}}
		submitLabel="Speichern"
		onsubmit={handleSubmit}
		oncancel={() => goto('/aufgaben')}
		{submitting}
	/>
{/if}
