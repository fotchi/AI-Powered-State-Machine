from flync_pipeline.etape4_developpeur.commun import build_shared_context

def main():
    ctx = build_shared_context(use_rag=False)
    candidates = ["FLYNCModel", "DeploymentUnion", "FLYNCChannelConfig", "FLYNCCommunicationConfig"]
    for name in candidates:
        ci = ctx.class_lookup.get(name)
        if not ci:
            print(f"{name} : introuvable")
            continue
        print(f"=== {name} ===")
        for f in ci.fields:
            print("  field:", f.name, "|", f.type_str)
        for v in ci.validators:
            print("  validator:", v.method_name)

if __name__ == "__main__":
    main()