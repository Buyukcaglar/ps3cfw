----------------
REPORTING ISSUES
----------------

To report bugs you can do it directly in my Tweet @xXEvilnatXx or in my official thread on PSX-Place

To create a report, do the following:
	- Check the CFW after a CLEAN install
	- Do not have any plugin enabled
		* At most ONLY have webMAN MOD enabled (Check for bugs with and without it enabled)
	- Report what specific error code/bug/data occurs
	- Report what was being done at the time of the issue


--------------
ENCRYPTED ISOs
--------------

To load an encrypted ISO from FAT32/exFAT/NTFS filesystem drive or PS3's internal HDD, you need to put the ISO in a folder called 'PS3ISO' in the root of the drive

The key MUST BE in the same folder as the ISO and with the same name but with extension '.key' instead '.iso'

For example:
	My ISO file:  x:/PS3ISO/Terraria_EUR.iso
	My KEY file:  x:/PS3ISO/Terraria_EUR.key
	My DKEY file: x:/PS3ISO/Terraria_EUR.dkey

	My ISO file:  /dev_hdd0/PS3ISO/Terraria_EUR.iso
	My KEY file:  /dev_hdd0/PS3ISO/Terraria_EUR.key
	My DKEY file: /dev_hdd0/PS3ISO/Terraria_EUR.dkey

If your ISO is not encrypted do not use a key file, this will confuse Cobra and it will try to decrypt it on-the-fly

Otherwise if you want to load an encrypted ISO from external exFAT/NTFS filesystem drive, you will need to use prepISO once to copy ISO data and disckey file to /dev_hdd0/tmp/wmtmp. ISO and key must be the same as with FAT32 filesystem

For NTFS/exFAT you can put '.dkey' file, prepISO will transform it to '.key' format for Cobra decryption on-the-fly

-Evilnat-