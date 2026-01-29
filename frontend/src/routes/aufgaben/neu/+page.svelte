<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { createApiClient, ApiError } from '$lib/api/client';
	import { apiBaseUrl, apiKey } from '$lib/stores/config';
	import { showToast } from '$lib/stores/toast';
	import type { Room, TaskCreate } from '$lib/api/types';
	import TaskForm from '$lib/components/tasks/TaskForm.svelte';
	import Loading from '$lib/components/shared/Loading.svelte';

	let rooms = $state<Room[]>([]);
	let loading = $state(true);
	let submitting = $state(false);

	onMount(async () => {
		try {
			const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
			rooms = await client.rooms.list();
		} catch {
			showToast('Fehler beim Laden der Räume', 'error');
		} finally {
			loading = false;
		}
	});

	async function handleSubmit(data: TaskCreate) {
		submitting = true;
		try {
			const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
			await client.tasks.create(data as TaskCreate);
			showToast('Aufgabe erstellt', 'success');
			goto('/aufgaben');
		} catch (e) {
			showToast(e instanceof ApiError ? e.detail : 'Fehler beim Erstellen', 'error');
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head>
	<title>Neue Aufgabe - ChoreQuest</title>
</svelte:head>

<h1 class="text-2xl font-bold mb-6">Neue Aufgabe</h1>

{#if loading}
	<Loading />
{:else}
	<TaskForm
		{rooms}
		submitLabel="Erstellen"
		onsubmit={handleSubmit}
		oncancel={() => goto('/aufgaben')}
		{submitting}
	/>
{/if}
