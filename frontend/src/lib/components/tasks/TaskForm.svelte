<script lang="ts">
	import type { Room, TaskCreate, TaskUpdate, Recurrence } from '$lib/api/types';
	import Button from '$lib/components/ui/Button.svelte';
	import Card from '$lib/components/ui/Card.svelte';

	interface Props {
		rooms: Room[];
		initial?: {
			title?: string;
			description?: string | null;
			room_id?: number;
			base_points?: number;
			estimated_minutes?: number;
			recurrence?: Recurrence;
			recurrence_day?: number | null;
			is_active?: boolean;
		};
		submitLabel?: string;
		onsubmit: (data: TaskCreate | TaskUpdate) => void;
		oncancel: () => void;
		submitting?: boolean;
	}

	let {
		rooms,
		initial = {},
		submitLabel = 'Speichern',
		onsubmit,
		oncancel,
		submitting = false
	}: Props = $props();

	let title = $state(initial.title ?? '');
	let description = $state(initial.description ?? '');
	let room_id = $state(initial.room_id ?? (rooms[0]?.id ?? 0));
	let base_points = $state(initial.base_points ?? 10);
	let estimated_minutes = $state(initial.estimated_minutes ?? 15);
	let recurrence = $state<Recurrence>(initial.recurrence ?? 'once');
	let recurrence_day = $state<number | null>(initial.recurrence_day ?? null);
	let is_active = $state(initial.is_active ?? true);

	const weekdays = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'];

	function handleSubmit() {
		onsubmit({
			title,
			description: description || null,
			room_id,
			base_points,
			estimated_minutes,
			recurrence,
			recurrence_day: recurrence === 'weekly' ? recurrence_day : null,
			is_active
		});
	}
</script>

<Card>
	<form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-4">
		<div>
			<label for="title" class="block text-sm font-medium mb-1">Titel *</label>
			<input
				id="title"
				type="text"
				bind:value={title}
				required
				class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500"
				placeholder="z.B. Küche wischen"
			/>
		</div>

		<div>
			<label for="description" class="block text-sm font-medium mb-1">Beschreibung</label>
			<textarea
				id="description"
				bind:value={description}
				rows={2}
				class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500"
				placeholder="Optionale Details..."
			></textarea>
		</div>

		<div class="grid grid-cols-2 gap-4">
			<div>
				<label for="room" class="block text-sm font-medium mb-1">Raum *</label>
				<select
					id="room"
					bind:value={room_id}
					class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500"
				>
					{#each rooms as room (room.id)}
						<option value={room.id}>{room.name}</option>
					{/each}
				</select>
			</div>

			<div>
				<label for="recurrence" class="block text-sm font-medium mb-1">Wiederholung</label>
				<select
					id="recurrence"
					bind:value={recurrence}
					class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500"
				>
					<option value="once">Einmalig</option>
					<option value="daily">Täglich</option>
					<option value="weekly">Wöchentlich</option>
					<option value="monthly">Monatlich</option>
				</select>
			</div>
		</div>

		{#if recurrence === 'weekly'}
			<div>
				<label for="recurrence-day" class="block text-sm font-medium mb-1">Wochentag</label>
				<select
					id="recurrence-day"
					bind:value={recurrence_day}
					class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500"
				>
					{#each weekdays as day, i}
						<option value={i}>{day}</option>
					{/each}
				</select>
			</div>
		{/if}

		{#if recurrence === 'monthly'}
			<div>
				<label for="recurrence-day-monthly" class="block text-sm font-medium mb-1">Tag im Monat</label>
				<input
					id="recurrence-day-monthly"
					type="number"
					min={1}
					max={28}
					bind:value={recurrence_day}
					class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500"
				/>
			</div>
		{/if}

		<div class="grid grid-cols-2 gap-4">
			<div>
				<label for="points" class="block text-sm font-medium mb-1">Punkte</label>
				<input
					id="points"
					type="number"
					min={1}
					max={100}
					bind:value={base_points}
					class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500"
				/>
			</div>
			<div>
				<label for="minutes" class="block text-sm font-medium mb-1">Geschätzte Minuten</label>
				<input
					id="minutes"
					type="number"
					min={1}
					max={240}
					bind:value={estimated_minutes}
					class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500"
				/>
			</div>
		</div>

		{#if initial.title}
			<div class="flex items-center gap-2">
				<input id="active" type="checkbox" bind:checked={is_active} class="rounded" />
				<label for="active" class="text-sm font-medium">Aktiv</label>
			</div>
		{/if}

		<div class="flex gap-3 justify-end pt-2">
			<Button variant="secondary" onclick={oncancel}>Abbrechen</Button>
			<Button type="submit" disabled={!title || !room_id || submitting}>
				{submitting ? 'Speichert...' : submitLabel}
			</Button>
		</div>
	</form>
</Card>
