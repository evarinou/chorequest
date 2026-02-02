<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		class?: string;
		children: Snippet;
	}

	let { class: className = '', children }: Props = $props();
</script>

<div class="pixel-border bg-parchment-50 dark:bg-crt-panel p-4 {className}">
	{@render children()}
</div>
