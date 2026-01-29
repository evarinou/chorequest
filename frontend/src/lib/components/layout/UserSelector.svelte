<script lang="ts">
	import { users, selectedUserId } from '$lib/stores/user';
	import { mdiAccountCircle } from '@mdi/js';
	import Icon from '$lib/components/ui/Icon.svelte';

	function handleChange(e: Event) {
		const target = e.target as HTMLSelectElement;
		const val = target.value;
		$selectedUserId = val ? Number(val) : null;
	}
</script>

<div class="flex items-center gap-2">
	<Icon path={mdiAccountCircle} size={20} class="text-gray-400" />
	<select
		value={$selectedUserId ?? ''}
		onchange={handleChange}
		class="text-sm bg-transparent border border-gray-300 dark:border-gray-600 rounded-lg px-2 py-1.5 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800"
	>
		<option value="">Benutzer wählen</option>
		{#each $users as user (user.id)}
			<option value={user.id}>{user.display_name || user.username}</option>
		{/each}
	</select>
</div>
