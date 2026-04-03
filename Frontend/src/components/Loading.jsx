function Loading({ size = 'md', fullScreen = false }) {
    const sizes = {
        sm: 'h-4 w-4 border-[3px]',
        md: 'h-8 w-8 border-[3px]',
        lg: 'h-12 w-12 border-[4px]',
        xl: 'h-16 w-16 border-[4px]',
    };

    const spinner = (
        <div className="relative flex items-center justify-center">
            <div className={`${sizes[size]} animate-spin rounded-full border-white/10 border-t-amber-400`} />
            <div className="absolute h-2 w-2 rounded-full bg-amber-400" />
        </div>
    );

    if (fullScreen) {
        return (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#05050d]/92 backdrop-blur-xl">
                <div className="smoke-panel rounded-[2rem] px-10 py-10 text-center">
                    {spinner}
                    <p className="mt-5 font-display text-2xl font-bold tracking-[-0.04em] text-white">Chargement</p>
                    <p className="mt-2 text-sm text-white/48">Préparation de l&apos;interface…</p>
                </div>
            </div>
        );
    }

    return spinner;
}

export default Loading;
