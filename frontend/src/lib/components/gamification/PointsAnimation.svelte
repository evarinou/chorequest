<script lang="ts">
	interface Props {
		points: number;
	}

	let { points }: Props = $props();
</script>

<div class="fixed inset-0 flex items-center justify-center pointer-events-none z-50">
	<div class="animate-float-up text-4xl font-bold text-accent-500 drop-shadow-lg">
		+{points}
	</div>
</div>
