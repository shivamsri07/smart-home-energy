// src/features/dashboard/AddDeviceDialog.tsx
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createDevice } from "@/api/deviceApi";
import { toast } from "sonner";

interface AddDeviceDialogProps {
  onDeviceAdded: () => void;
}

export function AddDeviceDialog({ onDeviceAdded }: AddDeviceDialogProps) {
  const [name, setName] = useState("");
  const [isOpen, setIsOpen] = useState(false);

  const handleSubmit = async () => {
    if (!name) {
      toast.error("Device name cannot be empty.");
      return;
    }
    try {
      await createDevice(name);
      toast.success("Device created successfully!");
      onDeviceAdded(); // This will tell the parent component to refresh its device list
      setIsOpen(false); // Close the dialog
      setName(""); // Reset form
    } catch (error) {
      toast.error("Failed to create device.");
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button>Add New Device</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Add New Device</DialogTitle>
          <DialogDescription>
            Give your new device a name. Click save when you're done.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="name" className="text-right">Name</Label>
            <Input id="name" value={name} onChange={(e) => setName(e.target.value)} className="col-span-3" />
          </div>
        </div>
        <DialogFooter>
          <Button type="submit" onClick={handleSubmit}>Save device</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}