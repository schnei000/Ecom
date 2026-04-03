export function formatCurrency(amount = 0) {
    return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: 'USD',
    }).format(Number(amount) || 0);
}

export function formatDate(value) {
    if (!value) return '—';
    try {
        return new Date(value).toLocaleDateString('fr-FR', {
            day: '2-digit',
            month: 'long',
            year: 'numeric',
        });
    } catch {
        return value;
    }
}

export function formatDateTime(value) {
    if (!value) return '—';
    try {
        return new Date(value).toLocaleString('fr-FR', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    } catch {
        return value;
    }
}
