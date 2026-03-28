<script lang="ts">
  let {
    isOpen = false,
    title = 'Confirm',
    message,
    confirmText = 'Confirm',
    cancelText = 'Cancel',
    variant = 'danger',
    onconfirm,
    oncancel,
  }: {
    isOpen?: boolean
    title?: string
    message: string
    confirmText?: string
    cancelText?: string
    variant?: 'danger' | 'warning' | 'info'
    onconfirm?: () => void
    oncancel?: () => void
  } = $props()

  function handleConfirm() {
    onconfirm?.()
  }

  function handleCancel() {
    oncancel?.()
  }

  function handleBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget) {
      handleCancel()
    }
  }

  const variantClasses = $derived.by(() => {
    if (variant === 'danger') return 'btn-error'
    if (variant === 'warning') return 'btn-warning'
    return 'btn-info'
  })
</script>

{#if isOpen}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    onclick={handleBackdropClick}
    role="dialog"
    aria-modal="true"
  >
    <div class="bg-base-100 rounded-lg shadow-xl w-full max-w-md p-6 space-y-4">
      <h3 class="text-xl font-bold">{title}</h3>

      <p class="text-base-content/80">{message}</p>

      <div class="flex justify-end gap-2">
        <button
          class="btn btn-ghost"
          onclick={handleCancel}
        >
          {cancelText}
        </button>
        <button
          class="btn {variantClasses}"
          onclick={handleConfirm}
        >
          {confirmText}
        </button>
      </div>
    </div>
  </div>
{/if}
