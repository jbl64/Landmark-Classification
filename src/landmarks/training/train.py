import torch
from collections import defaultdict


def run_model(model, train_loader, val_loader, criterion, optimizer, scheduler, device, epochs):
    best_val = 0.0

    for epoch in range(epochs):
        print(f"\nepoch={epoch}")

        train_acc = train_one_epoch(model, train_loader, optimizer, criterion, device)
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)

        print(f"Train Acc: {train_acc:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}")

        scheduler.step()

        if val_acc > best_val:
            best_val = val_acc
            print(f"New best val: {best_val:.4f}")
            torch.save(model.state_dict(), "best_model.pth")

        if epoch % 2 == 0:
            compute_per_class_accuracy(model, val_loader, device)


def train_one_epoch(model, loader, optimizer, criterion, device):
    model.train()
    correct, total = 0, 0

    for i, (x, y) in enumerate(loader):
        # print batch num ever 100 batches
        if i  % 100 == 0:
            print(f"batch {i}/{len(loader)}")

        x, y = x.to(device), y.to(device)

        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()

        preds = logits.argmax(dim=1)
        correct += (preds == y).sum().item()
        total += x.size(0)

    return correct / total


def evaluate(model, loader, criterion, device):
    model.eval()
    val_loss, correct, total = 0.0, 0, 0

    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            val_loss += criterion(logits, y).item()
            correct += (logits.argmax(dim=1) == y).sum().item()
            total += y.size(0)

    return val_loss / len(loader), correct / total


def compute_per_class_accuracy(model, loader, device):
    ### Calculate per-class accuracy of model this epoch
    class_correct = defaultdict(int)
    class_total = defaultdict(int)

    model.eval()
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            preds = logits.argmax(dim=1)

            for yi, pi in zip(y, preds):
                cls = yi.item()
                class_total[cls] += 1
                if yi == pi:
                    class_correct[cls] += 1

    print("\nPer-class accuracy:")
    for cls in sorted(class_total):
        acc = class_correct[cls] / class_total[cls]
        print(f"class {cls}: {acc:.3f}")