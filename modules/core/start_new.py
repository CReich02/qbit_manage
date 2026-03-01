from datetime import timedelta
from modules import util

logger = util.logger

class StartNew:
    def __init__(self, qbit_manager):
        self.qbt = qbit_manager
        self.config = qbit_manager.config
        self.client = qbit_manager.client
        self.stats_started = 0

        self.torrents_updated_start = []  # List of torrents started
        self.notify_attr_start = []  # List of single torrent attributes to send to notifiarr

        self.start()
        self.config.webhooks_factory.notify(self.torrents_updated_start, self.notify_attr_start, group_by="tag")

    def start(self):
        """Function used to start new torrents sorted by size"""
        if self.config.commands["start_new"]:
            logger.separator("Starting New Torrents", space=False, border=False)
            # Filter torrents by paused and sort by added_on
            if self.qbt.torrent_list:
                for torrent in self.qbt.torrent_list:
                    tracker = self.qbt.get_tags(self.qbt.get_tracker_urls(torrent.trackers))
                    t_name = torrent.name
                    t_category = torrent.category
                    # Start torrent if stopped and progress is 0
                    if (
                        torrent.progress == 0
                        and torrent.state_enum.is_stopped
                        and torrent.time_active < 10
                    ):
                        self.stats_started += 1
                        body = logger.print_line(
                            f"{'Not Starting' if self.config.dry_run else 'Starting'} [{tracker['tag']}] - {t_name}",
                            self.config.loglevel,
                        )
                        attr = {
                            "function": "start_new",
                            "title": "Starting Torrent",
                            "body": body,
                            "torrents": [t_name],
                            "torrent_tag": ", ".join(tracker["tag"]),
                            "torrent_category": t_category,
                            "torrent_tracker": tracker["url"],
                            "notifiarr_indexer": tracker["notifiarr"],
                        }
                        self.torrents_updated_start.append(t_name)
                        self.notify_attr_start.append(attr)
                        if not self.config.dry_run:
                            torrent.start()

            torrent_list = self.qbt.get_torrents({"status_filter": "paused", "sort": "added_on"})
            if torrent_list:
                for torrent in torrent_list:
                    tracker = self.qbt.get_tags(self.qbt.get_tracker_urls(torrent.trackers))
                    t_name = torrent.name
                    t_category = torrent.category
                    # Start torrent if stopped and progress is 0
                    if (
                        torrent.progress == 0
                        and not self.qbt.torrentinfo[t_name]["is_complete"]
                        and torrent.state_enum.is_stopped
                        and torrent.time_active < 60
                    ):
                        self.stats_started += 1
                        body = logger.print_line(
                            f"{'Not Starting' if self.config.dry_run else 'Starting'} [{tracker['tag']}] - {t_name}",
                            self.config.loglevel,
                        )
                        attr = {
                            "function": "start_new",
                            "title": "Starting Torrent",
                            "body": body,
                            "torrents": [t_name],
                            "torrent_tag": ", ".join(tracker["tag"]),
                            "torrent_category": t_category,
                            "torrent_tracker": tracker["url"],
                            "notifiarr_indexer": tracker["notifiarr"],
                        }
                        self.torrents_updated_start.append(t_name)
                        self.notify_attr_start.append(attr)
                        if not self.config.dry_run:
                            torrent.start()
