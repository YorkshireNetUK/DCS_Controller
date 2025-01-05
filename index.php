<?php
\$status_file = "tone_status.json";

if (!file_exists(\$status_file)) {
    echo "No data available.";
    exit;
}

\$data = json_decode(file_get_contents(\$status_file), true);
if (!\$data) {
    echo "Unable to parse status data.";
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YorkshireSVX Monitor</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background-color: #1e1e2f;
            color: #ffffff;
        }
        header {
            background-color: #2a2a3b;
            padding: 1rem 2rem;
            text-align: center;
            font-size: 1.5rem;
            color: #ffffff;
            border-bottom: 2px solid #444;
        }
        header span {
            color: #61dafb;
        }
        table {
            width: 90%;
            margin: 2rem auto;
            border-collapse: collapse;
            background-color: #2a2a3b;
            border-radius: 8px;
            overflow: hidden;
        }
        th, td {
            padding: 1rem;
            text-align: center;
        }
        th {
            background-color: #444;
            color: #ffffff;
        }
        td {
            background-color: #333;
        }
        tr:nth-child(even) td {
            background-color: #292939;
        }
        tr:hover td {
            background-color: #444;
        }
        footer {
            background-color: #2a2a3b;
            padding: 1rem;
            text-align: center;
            color: #ccc;
            font-size: 0.9rem;
            border-top: 2px solid #444;
        }
        footer a {
            color: #61dafb;
            text-decoration: none;
        }
        footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <header>
        Yorkshire<span>SVX</span> Monitor
    </header>
    <main>
        <h2 style="text-align:center;">Live Status</h2>
        <table>
            <tr>
                <th>Callsign</th>
                <th>Status</th>
                <th>Last Update</th>
            </tr>
            <?php foreach (\$data as \$callsign => \$info): ?>
                <tr>
                    <td><?= htmlspecialchars(\$callsign) ?></td>
                    <td><?= ucfirst(htmlspecialchars(\$info['status'])) ?></td>
                    <td><?= htmlspecialchars(\$info['timestamp']) ?></td>
                </tr>
            <?php endforeach; ?>
        </table>
    </main>
    <footer>
        YorkshireSVX Monitor | <a href="mailto:support@svxlink.uk">support@svxlink.uk</a>
    </footer>
</body>
</html>