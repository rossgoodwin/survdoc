until python arise.py 10.0.0.3; do
    echo "Process crashed with exit code $?. Respawning..." >&2
    sleep 5
done