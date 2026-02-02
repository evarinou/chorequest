<script lang="ts">
	import { onMount } from 'svelte';
	import { createApiClient, ApiError } from '$lib/api/client';
	import { apiBaseUrl, apiKey } from '$lib/stores/config';
	import { showToast } from '$lib/stores/toast';
	import type { Room, RoomUpdate } from '$lib/api/types';
	import Card from '$lib/components/ui/Card.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Icon from '$lib/components/ui/Icon.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Loading from '$lib/components/shared/Loading.svelte';
	import ErrorMessage from '$lib/components/shared/ErrorMessage.svelte';
	import { mdiPencil } from '@mdi/js';

	let rooms = $state<Room[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let editRoom = $state<Room | null>(null);
	let editMultiplier = $state(1.0);
	let editIcon = $state('');
	let editSortOrder = $state(0);
	let editModalOpen = $state(false);
	let saving = $state(false);

	async function loadData() {
		loading = true;
		error = null;
		try {
			const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
			rooms = await client.rooms.list();
		} catch (e) {
			error = e instanceof ApiError ? e.detail : 'Fehler beim Laden';
		} finally {
			loading = false;
		}
	}

	function openEdit(room: Room) {
		editRoom = room;
		editMultiplier = room.point_multiplier;
		editIcon = room.icon;
		editSortOrder = room.sort_order;
		editModalOpen = true;
	}

	async function saveEdit() {
		if (!editRoom) return;
		saving = true;
		try {
			const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
			await client.rooms.update(editRoom.id, {
				icon: editIcon,
				point_multiplier: editMultiplier,
				sort_order: editSortOrder
			} as RoomUpdate);
			editModalOpen = false;
			showToast('Zone aktualisiert', 'success');
			await loadData();
		} catch (e) {
			showToast(e instanceof ApiError ? e.detail : 'Fehler beim Speichern', 'error');
		} finally {
			saving = false;
		}
	}

	onMount(loadData);
</script>

<svelte:head>
	<title>Räume - ChoreQuest</title>
</svelte:head>

<h1 class="text-sm mb-4">ZONEN-KARTE</h1>

<div class="flex items-center gap-2 mb-6 text-sm text-parchment-400 dark:text-crt-green/60">
	<span>📡</span>
	<span>Zonen werden aus Home Assistant synchronisiert.</span>
</div>

{#if loading}
	<Loading />
{:else if error}
	<ErrorMessage message={error} onretry={loadData} />
{:else if rooms.length === 0}
	<Card class="text-center py-8">
		<p class="text-parchment-400 dark:text-crt-green/60">Keine Zonen. Synchronisiere mit Home Assistant.</p>
	</Card>
{:else}
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
		{#each rooms.toSorted((a, b) => a.sort_order - b.sort_order) as room (room.id)}
			<Card class="flex items-start justify-between">
				<div>
					<h3 class="text-[10px]" style="font-family: 'Press Start 2P', monospace;">{room.name.toUpperCase()}</h3>
					<div class="flex items-center gap-2 mt-2">
						{#if room.point_multiplier !== 1.0}
							<Badge variant="warning">{room.point_multiplier}x XP</Badge>
						{:else}
							<Badge>1.0x XP</Badge>
						{/if}
						{#if room.ha_area_id}
							<Badge variant="success">HA</Badge>
						{/if}
					</div>
					<p class="text-xs text-parchment-400 dark:text-crt-green/50 mt-2">Icon: {room.icon}</p>
				</div>
				<button
					onclick={() => openEdit(room)}
					class="p-2 text-parchment-400 hover:text-nes-gold dark:text-crt-green/60 dark:hover:text-crt-green"
				>
					<Icon path={mdiPencil} size={18} />
				</button>
			</Card>
		{/each}
	</div>
{/if}

<Modal open={editModalOpen} title="ZONE BEARBEITEN" onclose={() => { editModalOpen = false; }}>
	{#if editRoom}
		<div class="space-y-4">
			<div>
				<label for="edit-icon" class="block text-[9px] mb-1" style="font-family: 'Press Start 2P', monospace;">ICON (MDI)</label>
				<input
					id="edit-icon"
					type="text"
					bind:value={editIcon}
					class="pixel-input"
					placeholder="mdi:room"
				/>
			</div>
			<div>
				<label for="edit-multiplier" class="block text-[9px] mb-1" style="font-family: 'Press Start 2P', monospace;">
					XP-MULTIPLIKATOR: {editMultiplier.toFixed(1)}x
				</label>
				<input
					id="edit-multiplier"
					type="range"
					min={0.5}
					max={3.0}
					step={0.1}
					bind:value={editMultiplier}
					class="w-full accent-nes-green"
				/>
				<div class="flex justify-between text-xs text-parchment-400 dark:text-crt-green/50">
					<span>0.5x</span>
					<span>3.0x</span>
				</div>
			</div>
			<div>
				<label for="edit-sort" class="block text-[9px] mb-1" style="font-family: 'Press Start 2P', monospace;">SORTIERUNG</label>
				<input
					id="edit-sort"
					type="number"
					min={0}
					bind:value={editSortOrder}
					class="pixel-input"
				/>
			</div>
			<div class="flex gap-3 justify-end">
				<Button variant="secondary" onclick={() => { editModalOpen = false; }}>ZURÜCK</Button>
				<Button onclick={saveEdit} disabled={saving}>
					{saving ? 'SPEICHERT...' : 'SPEICHERN'}
				</Button>
			</div>
		</div>
	{/if}
</Modal>
