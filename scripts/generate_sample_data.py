import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.services.sales_data_service import build_sample_data


def main():
    data = build_sample_data()
    print(f"Territories: {len(data['territories'])}")
    print(f"Accounts: {len(data['accounts'])}")
    print(f"Opportunities: {len(data['opportunities'])}")
    print(f"Playbooks: {len(data['playbooks'])}")


if __name__ == "__main__":
    main()
