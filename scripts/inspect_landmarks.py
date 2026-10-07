from datasets import load_dataset
from landmarks.data.dataset import load_metadata


def main():
    # load the dataset
    hf_dataset = load_metadata()
    landmarks = sorted(set(hf_dataset["train"]["landmark_id"]))

    print(f"Num landmarks: {len(landmarks)}")

    # load the id mapping dataset
    mapping_ds = load_dataset("visheratin/google_landmarks_places")["train"]

    # build id to country mapping
    print(mapping_ds[0])
    id_to_country = {int(x["id"]): (x["category_name"], x["country"]) for x in mapping_ds}

    print("\nLandmarks:")
    for l in landmarks:
        name, country = id_to_country.get(l, ("UNKNOWN", "UNKNOWN"))
        print(f"{l}: {name}, {country}")


if __name__ == "__main__":
    main()