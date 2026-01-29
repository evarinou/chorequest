<script lang="ts">
	interface Props {
		text?: string;
	}

	let { text = 'Laden...' }: Props = $props();
</script>

<div class="flex flex-col items-center justify-center py-12 gap-3">
	<div class="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
	<p class="text-sm text-gray-500 dark:text-gray-400">{text}</p>
</div>
