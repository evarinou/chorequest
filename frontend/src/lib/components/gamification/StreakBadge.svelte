<script lang="ts">
	import { mdiFire } from '@mdi/js';
	import Icon from '$lib/components/ui/Icon.svelte';

	interface Props {
		streak: number;
		size?: 'sm' | 'md' | 'lg';
	}

	let { streak, size = 'sm' }: Props = $props();

	let colorClass = $derived(
		streak >= 14 ? 'text-red-500' :
		streak >= 7 ? 'text-orange-500' :
		'text-yellow-500'
	);

	let iconSize = $derived(
		size === 'lg' ? 28 :
		size === 'md' ? 22 :
		16
	);

	let textSize = $derived(
		size === 'lg' ? 'text-lg' :
		size === 'md' ? 'text-sm' :
		'text-xs'
	);
</script>

{#if streak > 0}
	<div class="inline-flex items-center gap-0.5 {colorClass}">
		<span class="animate-flame inline-block">
			<Icon path={mdiFire} size={iconSize} />
		</span>
		<span class="font-bold {textSize}">{streak}</span>
	</div>
{/if}
