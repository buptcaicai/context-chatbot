let _config_from_s3: { REMOTE_ENDPOINT: string } | null = null;

export async function loadConfigFromS3() {
    if (_config_from_s3) {
        return _config_from_s3;
    }
    const config = await fetch(`${import.meta.env.VITE_S3_CONFIG_URL}`, {
        headers: {
            "Content-Type": "application/json",
        },
        method: "GET",
    });
    _config_from_s3 = await config.json();
    console.log('_config_from_s3',_config_from_s3);
}

export async function getRemoteEndpoint() {
    const config = await loadConfigFromS3();
    return config?.REMOTE_ENDPOINT;
}
