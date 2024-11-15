//-----------------------------------------------------------------------
//             github.com/samisalreadytaken/csgo-benchmark
//-----------------------------------------------------------------------
//
// This file is an additional way to load map data.
// If no data from 'bm_mapname.nut' file is found, this file is checked for
// 'bm_mapname' motion data and 'Setup_mapname()' setup function.
//
// While testing the timings to determine when to spawn grenades,
// execute 'benchmark;bm_timer' in the console to start the timer.
//
// Use the commands to get setup lines
//    bm_mdl
//    bm_flash
//    bm_he
//    bm_molo
//    bm_smoke
//    bm_expl
//
// Use bm_list to print every saved line
//
// Restarting the round (mp_restartgame 1) will remove spawned models
//
/*
enum MDL
{
    FBIa, FBIb, FBIc, FBId, FBIe, FBIf, FBIg, FBIh,
    GIGNa, GIGNb, GIGNc, GIGNd,
    GSG9a, GSG9b, GSG9c, GSG9d,
    IDFb, IDFc, IDFd, IDFe, IDFf,
    SASa, SASb, SASc, SASd, SASe, SASf,
    ST6a, ST6b, ST6c, ST6d, ST6e, ST6g, ST6i, ST6k, ST6m,
    SWATa, SWATb, SWATc, SWATd,
    ANARa, ANARb, ANARc, ANARd,
    BALKa, BALKb, BALKc, BALKd, BALKe, BALKf, BALKg, BALKh, BALKi, BALKj,
    LEETa, LEETb, LEETc, LEETd, LEETe, LEETf, LEETg, LEETh, LEETi,
    PHXa, PHXb, PHXc, PHXd, PHXf, PHXg, PHXh,
    PRTa, PRTb, PRTc, PRTd,
    PROa, PROb, PROc, PROd,
    SEPa, SEPb, SEPc, SEPd,
    H_CT, H_T
}

enum POSE
{
    DEFAULT,
    ROM,
    A,
    PISTOL,
    RIFLE
}
*/

//---------------
//-----------------------------------------------------------------------
//                       CS2 Benchmark Resources
//-----------------------------------------------------------------------

// Updated weapon models for CS2
::WEAPONS <- {
    KNIFE_CT = "models/weapons/ct_knife/ct_knife.vmdl",
    KNIFE_T = "models/weapons/t_knife/t_knife.vmdl",
    AK47 = "models/weapons/ak47/ak47.vmdl",
    M4A4 = "models/weapons/m4a4/m4a4.vmdl",
    AWP = "models/weapons/awp/awp.vmdl",
    DEAGLE = "models/weapons/deagle/deagle.vmdl",
    USP = "models/weapons/usp/usp.vmdl"
};

// Updated grenade models
::GRENADES <- {
    FLASHBANG = "models/weapons/flashbang/flashbang.vmdl",
    HEGRENADE = "models/weapons/hegrenade/hegrenade.vmdl",
    SMOKEGRENADE = "models/weapons/smokegrenade/smokegrenade.vmdl",
    MOLOTOV = "models/weapons/molotov/molotov.vmdl",
    DECOY = "models/weapons/decoy/decoy.vmdl"
};

// Updated effects
::EFFECTS <- {
    EXPLOSION = "particles/explosion/explosion_grenade.vpcf",
    SMOKE = "particles/smoke/smoke_grenade.vpcf",
    FLASH = "particles/flash/flashbang_explosion.vpcf",
    MOLOTOV_FLAME = "particles/molotov/molotov_flame.vpcf"
};

// Updated sounds
::SOUNDS <- {
    EXPLOSION = "Weapon_Explode.Default",
    FLASH = "Weapon_Flashbang.Explode",
    SMOKE = "Weapon_Smokegrenade.Explode",
    MOLOTOV = "Weapon_Molotov.Detonate"
};
