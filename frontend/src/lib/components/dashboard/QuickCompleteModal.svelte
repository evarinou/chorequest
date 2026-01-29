<script lang="ts">
	import type { TaskInstanceWithDetails } from '$lib/api/types';
	import { users, selectedUserId } from '$lib/stores/user';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';

	interface Props {
		open: boolean;
		instance: TaskInstanceWithDetails | null;
		onclose: () => void;
		oncomplete: (instanceId: number, userId: number, notes: string) => void;
	}

	let { open, instance, onclose, oncomplete }: Props = $props();

	let userId = $state<number | null>(null);
	let notes = $state('');
	let submitting = $state(false);

	$effect(() => {
		if (open) {
			userId = $selectedUserId;
			notes = '';
			submitting = false;
		}
	});

	async function handleSubmit() {
		if (!instance || !userId) return;
		submitting = true;
		oncomplete(instance.id, userId, notes);
	}
</script>

<Modal {open} title="Aufgabe erledigen" {onclose}>
	{#if instance}
		<div class="space-y-4">
			<div>
				<p class="font-medium">{instance.task.title}</p>
				{#if instance.task.description}
					<p class="text-sm text-gray-500 dark:text-gray-400 mt-1">{instance.task.description}</p>
				{/if}
			</div>

			<div>
				<label for="user-select" class="block text-sm font-medium mb-1">Erledigt von</label>
				<select
					id="user-select"
					bind:value={userId}
					class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500"
				>
					<option value={null}>Benutzer wählen...</option>
					{#each $users as user (user.id)}
						<option value={user.id}>{user.display_name || user.username}</option>
					{/each}
				</select>
			</div>

			<div>
				<label for="notes" class="block text-sm font-medium mb-1">Notizen (optional)</label>
				<textarea
					id="notes"
					bind:value={notes}
					rows={2}
					class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500"
					placeholder="z.B. Backofen mitgeputzt..."
				></textarea>
			</div>

			<div class="flex gap-3 justify-end">
				<Button variant="secondary" onclick={onclose}>Abbrechen</Button>
				<Button onclick={handleSubmit} disabled={!userId || submitting}>
					{submitting ? 'Wird gespeichert...' : 'Erledigt!'}
				</Button>
			</div>
		</div>
	{/if}
</Modal>
