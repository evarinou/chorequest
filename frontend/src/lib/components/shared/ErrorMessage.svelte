<script lang="ts">
	import { mdiAlertCircle, mdiRefresh } from '@mdi/js';
	import Icon from '$lib/components/ui/Icon.svelte';
	import Button from '$lib/components/ui/Button.svelte';

	interface Props {
		message?: string;
		onretry?: () => void;
	}

	let { message = 'Ein Fehler ist aufgetreten.', onretry }: Props = $props();
</script>

<div class="flex flex-col items-center justify-center py-12 gap-4 text-center">
	<Icon path={mdiAlertCircle} size={48} class="text-danger-500" />
	<p class="text-gray-600 dark:text-gray-400">{message}</p>
	{#if onretry}
		<Button variant="secondary" onclick={onretry}>
			<Icon path={mdiRefresh} size={18} />
			Erneut versuchen
		</Button>
	{/if}
</div>
