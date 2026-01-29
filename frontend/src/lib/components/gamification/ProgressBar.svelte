<script lang="ts">
	interface Props {
		value: number;
		class?: string;
	}

	let { value, class: className = '' }: Props = $props();

	let clamped = $derived(Math.max(0, Math.min(100, value)));
</script>

<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 {className}">
	<div
		class="bg-primary-500 h-2 rounded-full transition-all duration-500"
		style="width: {clamped}%"
	></div>
</div>
